from enum import Enum
from evolutek.lib.status import RobotStatus
from evolutek.lib.utils.color import Color
from evolutek.lib.utils.task import async_task
from evolutek.lib.utils.wrappers import if_enabled
from time import sleep
from evolutek.lib.actuators.i2c_acts import I2CActsHandler, I2CActType, ESCVariation
from evolutek.lib.actuators.ax12 import AX12Controller
from evolutek.lib.indicators.lightning_mode import *

ARM_SERVOS = {
    11: {
        "ax12": {"up": 270,"down": 587,},
        "servos": {
            "tip": {"id": 13,"positions": {
                "flipped": 10,
                "opened": 100,
                "closed": 195,
            }},
            "flipper": {"id": 14,"positions": {
                "a": 0,
                "b": 186,
            }},
            "barrier": {"id": 15,"positions": {
                "stored": 168,
                "near": 120,
                "mid": 100,
                "far": 80,
            }}
        }
    },

    12: {
        "ax12": {"up": 520,"down": 910,},
        "servos": {
            "tip": {"id": 10,"positions": {
                "flipped": 5,
                "opened": 95,
                "closed": 195,
            }},
            "flipper": {"id": 9,"positions": {
                "a": 0,
                "b": 186,
            }}
        }
    },

    13: {
        "ax12": {"up": 510,"down": 113,},
        "servos": {
            "tip": {"id": 5,"positions": {
                "flipped": 5,
                "opened": 90,
                "closed": 190,
            }},
            "flipper": {"id": 4,"positions": {
                "a": 0,
                "b": 186,
            }}
        }
    },

    14: {
        "ax12": {"up": 680,"down": 378,},
        "servos": {
            "tip": {"id": 2,"positions": {
                "flipped": 10,
                "opened": 90,
                "closed": 195,
            }},
            "flipper": {"id": 1,"positions": {
                "a": 0,
                "b": 186,
            }},
            "barrier": {"id": 3,"positions": {
                "stored": 5,
                "near": 50,
                "mid": 70,
                "far": 100,
            }}
        }
    }
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

    angle = servo["positions"][pos]
    servo_id = servo["id"]

    return self.actuators.servo_set_angle(servo_id, angle)

@if_enabled
@async_task
def move_arm(self, id, pos: str):
    id = int(id)

    if id not in ARM_SERVOS:
        return RobotStatus.error(f"Unknown arm {id}")

    if pos not in ARM_SERVOS[id]["ax12"]:
        return RobotStatus.error(f"Unknown position {pos}")

    angle = ARM_SERVOS[id]["ax12"][pos]
    return self.actuators.ax_move(id, angle)

@if_enabled
def move_tip(self, id, pos: str):
    return self.move_servo(id, "tip", pos)

@if_enabled
def move_flipper(self, id, pos: str):
    return self.move_servo(id, "flipper", pos)

@if_enabled
def move_barrier(self, id, pos: str):
    return self.move_servo(id, "barrier", pos)

@if_enabled
def move_tips(self, id: int, pos: str):
    results = []

    for arm_id, arm in ARM_SERVOS.items():
        if arm_id // 10 != int(id):
            continue

        if "tip" not in arm["servos"]:
            continue

        servo = arm["servos"]["tip"]

        if pos not in servo["positions"]:
            return RobotStatus.error(f"Unknown position {pos}")

        angle = servo["positions"][pos]
        servo_id = servo["id"]

        res = self.actuators.servo_set_angle(servo_id, angle)
        results.append(res)

    return RobotStatus.check(all(results))