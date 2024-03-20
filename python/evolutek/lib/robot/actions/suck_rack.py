from evolutek.lib.robot.robot_actions_imports import *
from math import pi


class Rack:
    def __init__(self, side, axe, pos) -> None:
        self.side = side
        self.axe = axe
        self.pos = pos


RACKS = [
    Rack(True,  'y', 1500), # Rack position: (1500, 0)
    Rack(False, 'y', 1500), # Rack position: (1500, 2000)
    Rack(False, 'x', 1000), # Rack position: (0, 1000)
    Rack(True,  'x', 1000), # Rack position: (3000, 1000)
]


@if_enabled
@async_task
def suck_rack(self, rack, recal_sensor, quantity=7):
    OFFSET = 182.5 # Distance between robot center and vacuum

    rack = RACKS[int(rack)]
    quantity = int(quantity)

    # Recalibrate
    self.recalibration(
        x = rack.axe == 'x', y = rack.axe == 'y',
        init=True,
        x_sensor=(recal_sensor if rack.axe != 'x' else "no"),
        y_sensor=(recal_sensor if rack.axe == 'x' else "no"),
        side_x = rack.side, side_y = rack.side, async_task=False
    )

    status = []

    forward_value = 30

    position = self.trajman.get_position()

    if rack.axe == 'x':
        GAP = 200
        LENGTH = 30*10-15 + GAP
        x = LENGTH if not rack.side else 3000 - LENGTH
        self.goto_avoid(x=x, y=position['y'], async_task=False, mirror=False)
        y = rack.pos - OFFSET if position['y'] < 1000 else rack.pos + OFFSET
        self.goto_avoid(x=x, y=y, async_task=False, mirror=False)
        self.goth(pi if rack.side else 0, async_task=False, mirror=False)
        self.goto_avoid(x=x-GAP if not rack.side else x+GAP, y=y, async_task=False, mirror=False)
        left_vacuum = rack.side
    else:
        y = OFFSET if rack.side else 2000 - OFFSET
        self.goto_avoid(x=position['x'], y=y, async_task=False, mirror=False)
        theta = pi if position['x'] < 1500 else 0
        self.goth(theta, async_task=False, mirror=False)
        self.goto_avoid(x=rack.pos - 30 * 5 + 15, y=y, async_task=False, mirror=False)
        left_vacuum = rack.side

    if left_vacuum:
        status.append(self.extend_left_vacuum(async_task=False))
    else:
        status.append(self.extend_right_vacuum(async_task=False))

    self.push_isol(async_task=False)
    sleep(0.5)

    for _ in range(quantity):
        status.append(self.turbine_on(async_task=False))
        sleep(1)
        status.append(self.turbine_off(async_task=False))
        status.append(self.forward(-forward_value, async_task=False))
        self.cherry_count += 1
        sleep(1)

    if left_vacuum:
        status.append(self.retract_left_vacuum(async_task=False))
    else:
        status.append(self.retract_right_vacuum(async_task=False))

    return RobotStatus.check(*status, score=0)
