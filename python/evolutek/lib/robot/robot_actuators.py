from enum import Enum
from evolutek.lib.status import RobotStatus
from evolutek.lib.utils.task import async_task
from evolutek.lib.utils.wrappers import if_enabled

from evolutek.lib.actuators.i2c_acts import I2CActsHandler, I2CActType
from evolutek.lib.actuators.ax12 import AX12Controller


ARM_SERVOS = {
    11: {
        "ax12": {"up": 270, "half": 450, "cursor": 530, "down": 587},
        "servos": {
            "tip": {
                "id": 13,
                "positions": {"flipped": 10, "opened": 100, "closed": 195},
            },
            "flipper": {
                "id": 14,
                "positions": {"a": 0, "b": 186},
            },
            "barrier": {
                "id": 15,
                "positions": {"stored": 168, "near": 120, "mid": 100, "far": 70},
            },
        },
    },

    12: {
        "ax12": {"up": 520, "half": 740, "down": 910},
        "servos": {
            "tip": {
                "id": 10,
                "positions": {"flipped": 5, "opened": 95, "closed": 195},
            },
            "flipper": {
                "id": 9,
                "positions": {"a": 0, "b": 186},
            },
        },
    },

    13: {
        "ax12": {"up": 510, "half": 290, "down": 113},
        "servos": {
            "tip": {
                "id": 5,
                "positions": {"flipped": 5, "opened": 90, "closed": 190},
            },
            "flipper": {
                "id": 4,
                "positions": {"a": 0, "b": 186},
            },
        },
    },

    14: {
        "ax12": {"up": 680, "half": 496, "cursor": 420, "down": 378},
        "servos": {
            "tip": {
                "id": 2,
                "positions": {"flipped": 10, "opened": 90, "closed": 195},
            },
            "flipper": {
                "id": 1,
                "positions": {"a": 0, "b": 186},
            },
            "barrier": {
                "id": 3,
                "positions": {"stored": 5, "near": 50, "mid": 70, "far": 100},
            },
        },
    },

    21: {
        "ax12": {"up": 350, "half": 530,"down": 655},
        "servos": {
            "tip": {
                "id": 13 + 16,
                "positions": {"flipped": 0, "opened": 85, "closed": 185},
            },
            "flipper": {
                "id": 14 + 16,
                "positions": {"a": 0, "b": 170},
            },
            "barrier": {
                "id": 15 + 16,
                "positions": {"stored": 162, "near": 120, "mid": 100, "far": 70},
            },
        },
    },

    22: {
        "ax12": {"up": 525, "half": 740, "down": 910},
        "servos": {
            "tip": {
                "id": 10 + 16,
                "positions": {"flipped": 15, "opened": 100, "closed": 198},
            },
            "flipper": {
                "id": 9 + 16,
                "positions": {"a": 0, "b": 180},
            },
        },
    },

    23: {
        "ax12": {"up": 500, "half": 280, "down": 110},
        "servos": {
            "tip": {
                "id": 5 + 16,
                "positions": {"flipped": 10, "opened": 95, "closed": 190},
            },
            "flipper": {
                "id": 4 + 16,
                "positions": {"a": 0, "b": 180},
            },
        },
    },

    24: {
        "ax12": {"up": 670, "half": 496, "down": 365},
        "servos": {
            "tip": {
                "id": 2 + 16,
                "positions": {"flipped": 21, "opened": 105, "closed": 195},
            },
            "flipper": {
                "id": 1 + 16,
                "positions": {"a": 0, "b": 180},
            },
            "barrier": {
                "id": 3 + 16,
                "positions": {"stored": 0, "near": 50, "mid": 70, "far": 100},
            },
        },
    },

    31: {
        "ax12": {"up": 350, "half": 530,"down": 660},
        "servos": {
            "tip": {
                "id": 13 + 32,
                "positions": {"flipped": 10, "opened": 100, "closed": 195},
            },
            "flipper": {
                "id": 14 + 32,
                "positions": {"a": 0, "b": 186},
            },
            "barrier": {
                "id": 15 + 32,
                "positions": {"stored": 165, "near": 120, "mid": 100, "far": 70},
            },
        },
    },

    32: {
        "ax12": {"up": 530, "half": 740, "down": 915},
        "servos": {
            "tip": {
                "id": 10 + 32,
                "positions": {"flipped": 15, "opened": 100, "closed": 195},
            },
            "flipper": {
                "id": 9 + 32,
                "positions": {"a": 0, "b": 170},
            },
        },
    },

    33: {
        "ax12": {"up": 555, "half": 348, "down": 175},
        "servos": {
            "tip": {
                "id": 5 + 32,
                "positions": {"flipped": 15, "opened": 95, "closed": 190},
            },
            "flipper": {
                "id": 4 + 32,
                "positions": {"a": 0, "b": 186},
            },
        },
    },

    34: {
        "ax12": {"up": 680, "half": 496, "down": 375},
        "servos": {
            "tip": {
                "id": 2 + 32,
                "positions": {"flipped": 10, "opened": 85, "closed": 195},
            },
            "flipper": {
                "id": 1 + 32,
                "positions": {"a": 0, "b": 170},
            },
            "barrier": {
                "id": 3 + 32,
                "positions": {"stored": 5, "near": 50, "mid": 70, "far": 100},
            },
        },
    },
}


# =========================================================
# STATE
# =========================================================

# état simple des bras
ARM_STATE = {
    11: {"pos": "down"},
    12: {"pos": "down"},
    13: {"pos": "down"},
    14: {"pos": "down"},
    21: {"pos": "down"},
    22: {"pos": "down"},
    23: {"pos": "down"},
    24: {"pos": "down"},
    31: {"pos": "down"},
    32: {"pos": "down"},
    33: {"pos": "down"},
    34: {"pos": "down"},
}

@if_enabled
@async_task
def move_servo(self, id, type: str, pos: str):
    id = int(id)

    if id not in ARM_SERVOS:
        return RobotStatus.return_status(RobotStatus.Failed)

    servos = ARM_SERVOS[id]["servos"]

    if type not in servos:
        return RobotStatus.return_status(RobotStatus.Failed)

    servo = servos[type]

    # Handle common typos
    if pos == "openned" or pos == "open":
        pos = "opened"

    if pos == "close":
        pos = "closed"

    if pos == "stow" or pos == "store":
        pos = "stored"

    if pos not in servo["positions"]:
        return RobotStatus.return_status(RobotStatus.Failed)

    # SAFETY RULE
    if type == "tip" and ARM_STATE[id]["pos"] == "up" and pos != "closed":
        return RobotStatus.return_status(RobotStatus.Failed)

    angle = servo["positions"][pos]
    servo_id = servo["id"]

    return self.actuators.servo_set_angle(servo_id, angle)

# =========================================================
# MOVE SINGLE SERVOS
# =========================================================

@if_enabled
@async_task
def move_arm(self, id, pos: str):
    id = int(id)

    if id not in ARM_SERVOS:
        return RobotStatus.return_status(RobotStatus.Failed)

    if pos not in ARM_SERVOS[id]["ax12"]:
        return RobotStatus.return_status(RobotStatus.Failed)

    angle = ARM_SERVOS[id]["ax12"][pos]

    res = self.actuators.ax_move(id, angle)

    # update state
    ARM_STATE[id]["pos"] = pos

    # AUTO SAFE BEHAVIOR
    arm = ARM_SERVOS[id]["servos"]

    if pos != "down":
        # force tip closed
        if "tip" in arm:
            tip = arm["tip"]
            self.actuators.servo_set_angle(
                tip["id"],
                tip["positions"]["closed"]
            )

        # force barrier stored
        if "barrier" in arm:
            bar = arm["barrier"]
            self.actuators.servo_set_angle(
                bar["id"],
                bar["positions"]["stored"]
            )

    return res

@if_enabled
@async_task
def move_tip(self, id, pos: str):
    return self.move_servo(id, "tip", pos, async_task=False)


@if_enabled
@async_task
def move_flipper(self, id, pos: str):
    return self.move_servo(id, "flipper", pos, async_task=False)


@if_enabled
@async_task
def move_barrier(self, id, pos: str):
    return self.move_servo(id, "barrier", pos, async_task=False)


@if_enabled
@async_task
def move_barriers(self, id: int, pos: str):
    results = []

    for arm_id, arm in ARM_SERVOS.items():
        if arm_id // 10 != int(id) % 10:
            continue

        if "barrier" not in arm["servos"]:
            continue

        res = self.move_barrier(arm_id, pos, async_task=False)
        results.append(res)

    return RobotStatus.check(*results)


@if_enabled
@async_task
def move_flippers(self, id: int, pos: str):
    results = []

    for arm_id, arm in ARM_SERVOS.items():
        if arm_id // 10 != int(id) % 10:
            continue

        if "flipper" not in arm["servos"]:
            continue

        res = self.move_flipper(arm_id, pos, async_task=False)
        results.append(res)

    return RobotStatus.check(*results)


# =========================================================
# MOVE WHOLE FACE
# =========================================================

@if_enabled
@async_task
def move_tips(self, id: int, pos: str):
    results = []

    for arm_id, arm in ARM_SERVOS.items():
        if arm_id // 10 != int(id) % 10:
            continue

        if "tip" not in arm["servos"]:
            continue

        res = self.move_tip(arm_id, pos, async_task=False)
        results.append(res)

    return RobotStatus.check(*results)


@if_enabled
@async_task
def move_arms(self, id: int, pos: str):
    results = []

    for arm_id, arm in ARM_SERVOS.items():
        # filtre par face (11/12/13/14 → face 1)
        if arm_id // 10 != int(id) % 10:
            continue

        res = self.move_arm(arm_id, pos, async_task=False)
        results.append(res)

    return RobotStatus.check(*results)


@if_enabled
@async_task
def move(self, id, pos: str):
    id = int(id)
    id_str = str(id)

    arm_positions = {"up", "half", "down", "cursor"}
    tip_positions = {"flipped", "open", "closed", "close", "openned", "opened"}
    barrier_positions = {"stored", "near", "mid", "far", "stow", "store"}
    flipper_positions = {"a", "b"}

    if len(id_str) == 1:
        # face: depending on pos, move arms, tips, barriers, or flippers
        if pos in arm_positions:
            return self.move_arms(id, pos, async_task=False)
        elif pos in tip_positions:
            return self.move_tips(id, pos, async_task=False)
        elif pos in barrier_positions:
            return self.move_barriers(id, pos, async_task=False)
        elif pos in flipper_positions:
            return self.move_flippers(id, pos, async_task=False)
        else:
            return RobotStatus.return_status(RobotStatus.Failed)
    elif len(id_str) == 2:
        # arm: depending on pos, move arm, tip, barrier, or flipper
        if pos in arm_positions:
            return self.move_arm(id, pos, async_task=False)
        elif pos in tip_positions:
            return self.move_tip(id, pos, async_task=False)
        elif pos in barrier_positions:
            return self.move_barrier(id, pos, async_task=False)
        elif pos in flipper_positions:
            return self.move_flipper(id, pos, async_task=False)
        else:
            return RobotStatus.return_status(RobotStatus.Failed)
    elif len(id_str) == 3:
        # servo: move the specific servo on the arm
        arm_id = id // 10
        servo_digit = id % 10
        servo_types = {1: "tip", 2: "flipper", 3: "barrier"}
        if servo_digit not in servo_types:
            return RobotStatus.return_status(RobotStatus.Failed)
        servo_type = servo_types[servo_digit]
        return self.move_servo(arm_id, servo_type, pos, async_task=False)
    else:
        return RobotStatus.return_status(RobotStatus.Failed)