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

### Event routing — pending (step 4)

The legacy publishes a single event pair on every task boundary:

```python
self.publish('%s_robot_started' % ROBOT, id=task.id)
...
self.publish('%s_robot_stopped' % ROBOT, id=task.id, **r)
```

After step 4 each thread publishes on its own category-specific pair:

```python
# in Robot.run_tasks(category):
self.publish('%s_%s_started' % (ROBOT, category), id=task.id)
...
self.publish('%s_%s_stopped' % (ROBOT, category), id=task.id, **r)
```

Concretely:
- `%s_move_started` / `%s_move_stopped` for trajman flows
- `%s_actuator_started` / `%s_actuator_stopped` for actuator flows

`event_waiter` must accept the event pair as a parameter so two consumers
can wait independently without race. The single-pair version was implicitly
tied to "one task at a time" and would race if both pairs fired close
together on the same shared events.

Wiring impact:
- `services/ai.py:53-57` — the five `event_waiter(...)` wrappers around
  `robot.goth` / `robot.goto_avoid` / `robot.global_goto_avoid` /
  `robot.goto_with_path` / `robot.recalibration` switch to the move event
  pair.
- `lib/ai/goals.py:69` — when `Action.parse` wraps a `handler == 'robot'`
  call in `event_waiter`, it picks the right pair based on which sub-handler
  (trajman vs actuator). Initial cut: keep `handler == 'robot'` semantics
  routed to **move** events (legacy default — these are the actions that
  used to invoke goto / forward / recal under cover of `handler: robot`),
  and add a dedicated `'actuator'` handler path that wires the actuator
  event pair. This keeps the existing strategies.json files working
  without modification.

### Parallel making() — pending (step 5)

The current `making()` is structurally `goto → for action in actions`. After
step 5, `Action` gains an optional `when` field:

| `when` value      | Behavior                                  |
|-------------------|-------------------------------------------|
| `'on_arrival'`    | run after the goto completes (legacy)     |
| `'in_transit'`    | run **while** the goto is in flight       |

Default is `'on_arrival'` so existing `strategies.json` files behave
identically. The `making()` loop launches the move and all `in_transit`
actions concurrently, joins on both event pairs, then loops over
`on_arrival` actions.

### Strategies config — pending (step 6)

A single new optional field per action:

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

Backwards-compatible: absent `when` ⇒ `'on_arrival'`.

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
