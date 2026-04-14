from enum import Enum
from evolutek.lib.status import RobotStatus
from evolutek.lib.utils.task import async_task
from evolutek.lib.utils.wrappers import if_enabled

from evolutek.lib.actuators.i2c_acts import I2CActsHandler, I2CActType
from evolutek.lib.actuators.ax12 import AX12Controller


ARM_SERVOS = {
    11: {
        "ax12": {"up": 270, "flip": 450,"down": 587},
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
                "positions": {"stored": 168, "near": 120, "mid": 100, "far": 80},
            },
        },
    },

    12: {
        "ax12": {"up": 520, "flip": 740, "down": 910},
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
        "ax12": {"up": 510, "flip": 290, "down": 113},
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
        "ax12": {"up": 680, "flip": 496, "down": 378},
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
}

@if_enabled
@async_task
def move_servo(self, id, type: str, pos: str):
    id = int(id)

    if id not in ARM_SERVOS:
        return RobotStatus.error(f"Unknown arm {id}")

    servos = ARM_SERVOS[id]["servos"]

    if type not in servos:
        return RobotStatus.error(f"{type} not on arm {id}")

    servo = servos[type]

    if pos not in servo["positions"]:
        return RobotStatus.error(f"Unknown position {pos}")

    # SAFETY RULE
    if type == "tip" and ARM_STATE[id]["pos"] == "up" and pos != "closed":
        return RobotStatus.error("Tip must stay closed when arm is up")

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
        return RobotStatus.error(f"Unknown arm {id}")

    if pos not in ARM_SERVOS[id]["ax12"]:
        return RobotStatus.error(f"Unknown position {pos}")

    angle = ARM_SERVOS[id]["ax12"][pos]

    res = self.actuators.ax_move(id, angle)

    # update state
    ARM_STATE[id]["pos"] = pos

    # AUTO SAFE BEHAVIOR
    arm = ARM_SERVOS[id]["servos"]

    if pos == "up":
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
def move_tip(self, id, pos: str):
    return self.move_servo(id, "tip", pos)


@if_enabled
def move_flipper(self, id, pos: str):
    return self.move_servo(id, "flipper", pos)


@if_enabled
def move_barrier(self, id, pos: str):
    return self.move_servo(id, "barrier", pos)


# =========================================================
# MOVE WHOLE FACE
# =========================================================

@if_enabled
def move_tips(self, id: int, pos: str):
    results = []

    for arm_id, arm in ARM_SERVOS.items():
        if arm_id // 10 != int(id):
            continue

        if "tip" not in arm["servos"]:
            continue

        tip = arm["servos"]["tip"]

        if pos not in tip["positions"]:
            return RobotStatus.error(f"Unknown position {pos}")

        angle = tip["positions"][pos]
        servo_id = tip["id"]

        res = self.actuators.servo_set_angle(servo_id, angle)
        results.append(res)

    return RobotStatus.check(all(results))


@if_enabled
def move_arms(self, id: int, pos: str):
    results = []

    for arm_id, arm in ARM_SERVOS.items():
        # filtre par face (11/12/13/14 → face 1)
        if arm_id // 10 != int(id):
            continue

        # vérifie position AX12
        if pos not in arm["ax12"]:
            return RobotStatus.error(
                f"Unknown ax12 position {pos} for arm {arm_id}"
            )

        angle = arm["ax12"][pos]

        res = self.actuators.ax_move(arm_id, angle)
        results.append(res)

        # update state
        ARM_STATE[arm_id]["pos"] = pos

        # SAFE BEHAVIOR identique à move_arm
        servos = arm["servos"]

        if pos == "up":
            # force tip closed
            if "tip" in servos:
                tip = servos["tip"]
                self.actuators.servo_set_angle(
                    tip["id"],
                    tip["positions"]["closed"]
                )

            # force barrier stored
            if "barrier" in servos:
                barrier = servos["barrier"]
                self.actuators.servo_set_angle(
                    barrier["id"],
                    barrier["positions"]["stored"]
                )

    return RobotStatus.check(all(results))