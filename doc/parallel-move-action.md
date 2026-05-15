# Parallel move + action — architecture note

Status: in-progress feature branch `feat/parallel-move-action` (off `holo-2026`).

This note describes the architectural reshape that lets a trajman move and
an actuator action run **at the same time** in the legacy stack. It is meant
as a design reference for reviewers (Kolte / Kmikaz / TheCrabe) before the
event-routing commit (step 4) lands.

## Problem

In the legacy stack, a goto and a `move_arm` cannot overlap. Four serializing
layers stack up to enforce strict one-at-a-time execution:

1. **AI loop (`services/ai.py:336-521`, `making()`)** is strictly sequential:
   `goto*` synchronously, then `for action in current_goal.actions`. No
   notion of "do this action while still moving".
2. **`event_waiter` (`lib/utils/wrappers.py:38-94`)** waits on a single
   `(start_event, stop_event)` pair per Robot.
3. **`Robot.current_task` (`services/robot.py:113-159`)** is a single slot,
   single `run_tasks` thread.
4. **`@async_task` (`lib/utils/task.py:35-60`)** silently drops a second
   task when the slot is occupied (logs a `print` and forgets the request).

Trajman primitives (`robot_trajman.py`) and actuator primitives
(`robot_actuators.py`) share the same `Robot` instance, so they share **all
four** layers.

## Approach A — per-category slots and events

Two orthogonal categories of work are introduced:

- `'move'` — anything driving the asserv / trajman (goto, goth, recal, …)
- `'actuator'` — anything driving servos / AX12 / I²C actuators (move_arm,
  move_servo, grab, prepare_grab, …)

Each category owns its own slot, its own polling thread, **and its own
cellaserv event pair**. The two flows are independent end-to-end.

```
            ┌───────────────────────────────────────────────────┐
            │                       Robot                       │
            │                                                   │
            │   current_tasks = {                               │
            │       'move':     None | Task,   ← trajman calls  │
            │       'actuator': None | Task,   ← servo/AX12     │
            │   }                                               │
            │                                                   │
            │   Thread(run_tasks, 'move')      ─┐               │
            │   Thread(run_tasks, 'actuator')  ─┤  one per slot │
            │                                  ─┘               │
            └───────────────────────────────────────────────────┘
                              │             │
              %s_move_started │             │ %s_actuator_started
              %s_move_stopped │             │ %s_actuator_stopped
                              ▼             ▼
                ┌─────────────────────┐  ┌─────────────────────────┐
                │ event_waiter('move')│  │event_waiter('actuator') │
                │  used by AI.goto*   │  │  used by Action.make()  │
                │  and Robot moves    │  │  when handler='actuator'│
                └─────────────────────┘  └─────────────────────────┘
```

### Slot routing — done (commit 2289e0e1)

`@async_task` becomes a **decorator factory**: each driver site declares its
category at import time.

```python
# lib/utils/task.py
def async_task(category):
    def decorator(method):
        @wraps(method)
        def wrapped(self, *args, **kwargs):
            ...
            if run_async:
                with self.lock:
                    if self.current_tasks[category] is None:
                        self.current_tasks[category] = task
                    else:
                        print('[TASK][%s] Already a current task ...' % category)
            else:
                return task.run()
        return wrapped
    return decorator
```

Driver tagging:

| File                       | Category    |
|----------------------------|-------------|
| `lib/robot/robot_trajman.py`  | `'move'`    |
| `lib/robot/robot_actuators.py`| `'actuator'`|
| `lib/robot/robot_actions.py`  | `'actuator'`|
| `lib/robot/intelli.py`        | `'actuator'`|

`robot_actions.py` is tagged `'actuator'` because its compound actions
(`grab`, `prepare_grab`, `cursor`, …) only chain `self.move(...)` calls
internally — no trajman primitive. They therefore belong on the actuator
slot.

### Event routing — done (step 4, commit 663b82db)

`Robot.run_tasks(category)` publishes per-category events:

```python
self.publish('%s_%s_started' % (ROBOT, category), id=task.id)
...
self.publish('%s_%s_stopped' % (ROBOT, category), id=task.id, **r)
```

Concretely:
- `%s_move_started` / `%s_move_stopped` for trajman flows
- `%s_actuator_started` / `%s_actuator_stopped` for actuator flows

`event_waiter` already took the event pair as a parameter, no change there.
What changed is the **callers**:
- `services/ai.py` — the four cellaserv events are declared at class level
  (`move_started`, `move_stopped`, `actuator_started`, `actuator_stopped`).
  The five `event_waiter` wrappers around `robot.goth` / `robot.goto_avoid`
  / `robot.global_goto_avoid` / `robot.goto_with_path` / `robot.recalibration`
  are wired to the move pair.
- `lib/ai/goals.py` — `Action.parse` routes `handler: robot` actions to the
  actuator pair when `when == 'in_transit'`, to the move pair otherwise
  (legacy parity).

### Parallel making() — done (step 5, commit 6d68125b)

`Action` carries a `when` field (`'in_transit' | 'on_arrival'`, default
`'on_arrival'`). `making()` pre-splits the goal's actions, starts a worker
thread that runs `in_transit` actions sequentially on the actuator slot,
runs navigation in a nested closure on the move slot, joins the worker,
then runs `on_arrival` actions:

```
                ┌─────────────┐
                │ split when  │
                └──────┬──────┘
                       │
            ┌──────────┴───────────┐
            │                      │
            ▼                      ▼
     ┌─────────────┐         ┌─────────────────┐
     │  move slot  │         │   actuator slot │
     │  navigation │         │  in_transit acts│
     └──────┬──────┘         └────────┬────────┘
            │                         │
            └────────── join ─────────┘
                       │
                       ▼
                ┌─────────────┐
                │ on_arrival  │
                │  actions    │
                └─────────────┘
```

The per-action handling was extracted into `AI._run_action(...)` so the
in_transit worker and the on_arrival loop share the same code path: status
filtering, scoring, abort/timeout/skip strategies.

State precedence on early return: nav state wins, then in_transit state.
Rationale: a failed nav usually means the match is being aborted, in which
case the in_transit failure is downstream of the same cause.

### Strategies config — done (step 6)

An action node in `strategies.json` now accepts:

| Field             | Type     | Default        | Meaning                                                         |
|-------------------|----------|----------------|-----------------------------------------------------------------|
| `handler`         | string?  | (none)         | `'robot'` / `'actuators'` / ... — cellaserv service to call     |
| `fct`             | string   | (required)     | RPC method name on the handler                                  |
| `args`            | object?  | (none)         | kwargs passed to the call                                       |
| `avoid_strategy`  | string?  | `'wait'`       | `'wait'` / `'timeout'` / `'skip'`                                |
| `score`           | int?     | 0              | points credited on `Done` / `Reached`                            |
| `timeout`         | float?   | (none)         | seconds, used by avoid_strategy and pathfinding fallback         |
| `when`            | string?  | `'on_arrival'` | `'in_transit'` runs concurrently with the goto; `'on_arrival'` after |

Example: raise an arm while moving, then grab on arrival.

```json
{
  "name": "raise_arm_while_moving",
  "actions": [
    { "handler": "robot", "fct": "move_arm",
      "args": { "id": 11, "pos": "up" }, "when": "in_transit" },
    { "handler": "robot", "fct": "grab",
      "args": { "face": 1 }, "when": "on_arrival" }
  ]
}
```

Routing inference for `handler: robot`:
- `when: in_transit` → wait on `actuator_started` / `actuator_stopped`
- `when: on_arrival` (or unset) → wait on `move_started` / `move_stopped`

Legacy strategies (no `when` field) keep the move-event semantics, so they
are 1:1 compatible.

Constraints on `in_transit` actions:
- They must target the actuator slot (a move can't overlap another move).
  In practice this means `handler: robot` with an actuator `fct` like
  `move_arm`, `grab`, `move_servo`, ... or `handler: actuators` directly.
- They run **sequentially among themselves** on the single actuator slot.
  N parallel actuator actions per goal is not supported — list them in
  order, the worker chains them.

## What is *not* changed by this branch

- `self.disabled` and `self.need_to_abort` remain single events, shared
  across categories. They represent "the whole robot is dead" / "abort
  everything", which is the desired semantics. Per-category abort is out of
  scope.
- The `print('[TASK][%s] Already a current task ...')` drop policy on a
  busy slot is preserved. The slot is still one-task-deep within a
  category; we did not introduce a queue. Two concurrent moves still race
  to the slot, last loser is dropped.
- `intelli.py` and `robot_actions.py`'s commented-out legacy (lines
  112-322 of `robot_actions.py`, a Python triple-string block) are not
  cleaned up.

## Known pre-existing issues (unrelated to this work)

- `lib/robot/robot_trajman.py` line 178 mixes tabs and spaces inside the
  `print("Reached")` indentation. Already broken on `holo-2026`; not
  touched here.

## Commits so far

| SHA       | Subject                                                |
|-----------|--------------------------------------------------------|
| 2289e0e1  | robot: split task slot by category (move/actuator)     |
| 1d77a983  | doc: parallel move+action architecture note            |
| 663b82db  | robot, ai: split cellaserv events per category         |
| 6d68125b  | ai, goals: parallel move + in_transit actions in making() |
