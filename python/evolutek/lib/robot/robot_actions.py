from evolutek.lib.status import RobotStatus
from evolutek.lib.utils.wrappers import if_enabled, use_queue
from evolutek.lib.robot.robot_trajman import RecalSensor
from evolutek.lib.utils.color import Color

from time import sleep
from math import pi

#########
# REEFS #
#########

@if_enabled
@use_queue
def get_reef(self):

    self.left_cup_holder_open(use_queue=False)
    self.right_cup_holder_open(use_queue=False)
    self.actuators.pumps_get([7, 8, 9, 10])

    sleep(0.25)

    self.trajman.move_trsl(300, 300, 300, 300, 0)

    sleep(1)

    status = RobotStatus.get_status(self.recal(0))
    if status != RobotStatus.NotReached:
        return RobotStatus.return_status(status)

    self.left_cup_holder_close(use_queue=False)
    self.right_cup_holder_close(use_queue=False)

    status = self.check_abort()
    if status != RobotStatus.Ok:
        return RobotStatus.return_status(status)

    sleep(0.25)

    status = RobotStatus.get_status(self.move_trsl(300, 300, 300, 300, 1))
    if status != RobotStatus.Reached:
        return RobotStatus.return_status(status)

    return RobotStatus.return_status(RobotStatus.Done)


@if_enabled
@use_queue
def start_lighthouse(self):

    self.left_cup_holder_open(use_queue=False) if self.side else self.right_cup_holder_open(use_queue=False)
    sleep(0.25)

    status = RobotStatus.get_status(self.goto_avoid(x=180, y=2875, use_queue=False))
    if status != RobotStatus.Reached:
        self.left_cup_holder_close(use_queue=False) if self.side else self.right_cup_holder_close(use_queue=False)
        return RobotStatus.return_status(status)

    status = self.get_status(self.goto_avoid(x=200, y=2600, use_queue=False))
    self.left_cup_holder_close(use_queue=False) if self.side else self.right_cup_holder_close(use_queue=False)

    return RobotStatus.return_status(status if status != RobotStatus.Reached else RobotStatus.Done)


@if_enabled
@use_queue
def push_windsocks(self):

    self.recal(0)
    self.right_arm_open(use_queue=False) if self.side else self.left_arm_open(use_queue=False)

    sleep(0.25)

    speeds = self.trajman.get_speeds()
    self.trajman.set_trsl_max_speed(750)
    self.trajman.set_trsl_acc(300)
    self.trajman.set_trsl_dec(300)


    status = RobotStatus.get_status(self.goto_avoid(x=1825, y=720, use_queue=False))
    if status != RobotStatus.Reached:
        self.right_arm_close(use_queue=False) if self.side else self.left_arm_close(use_queue=False)
        self.trajman.set_trsl_max_speed(speeds['trmax'])
        self.trajman.set_trsl_acc(speeds['tracc'])
        self.trajman.set_trsl_dec(speeds['trdec'])
        return RobotStatus.return_status(status)

    if self.side:
        self.right_arm_push(use_queue=False)
        sleep(0.25)
        self.right_arm_close(use_queue=False)
    else:
        self.left_arm_push(use_queue=False)
        sleep(0.25)
        self.left_arm_close(use_queue=False)

    self.trajman.set_trsl_max_speed(speeds['trmax'])
    self.trajman.set_trsl_acc(speeds['tracc'])
    self.trajman.set_trsl_dec(speeds['trdec'])

    return RobotStatus.return_status(RobotStatus.Done)


@if_enabled
@use_queue
def drop_start_sorting(self):

    # TODO Handle end position
    # TODO Handle both sides
    # TODO Count points

    # Start position: 200 400 pi/2

    status = self.recalibration(x=False, y=True, x_sensor=RecalSensor.Left, use_queue=False)
    if status != RobotStatus.Done: return RobotStatus.return_status(status)

    # First set of front buoys
    x=600
    status = self.goto_avoid(x=x, y=250, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(status)
    status = self.goth(theta=-pi/2, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(status)
    status = self.goto(x=x, y=180, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(status)
    sleep(0.2)
    self.pumps_drop(ids='5,6', use_queue=False)
    status = self.goto_avoid(x=x, y=250, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(status)

    # Second set of front buoys
    x=1010
    status = self.goth(theta=0, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(status)
    status = self.goto_avoid(x=x, y=250, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(status)
    status = self.goth(theta=-pi/2, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(status)
    status = self.goto(x=x, y=180, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(status)
    sleep(0.2)
    self.pumps_drop(ids='2,3', use_queue=False)
    status = self.goto_avoid(x=x, y=350, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(status)

    # First buoy of the front arm
    self.front_arm_open(use_queue=False)
    sleep(0.5)
    status = self.goto(x=x, y=250, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(status)
    sleep(0.2)
    self.pumps_drop(ids='1,3', use_queue=False)
    status = self.goto_avoid(x=x, y=350, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(status)

    # Possible arrangements
    # 1: R R G G
    # 2: R G R G
    # 3: R G G R
    reef_arrangement = 1
    def check_arrangement(colors, arrangement):
        colors = list(map(lambda c: Color.get_by_name(c), colors))
        for i in range(4):
            if colors[i] != Color.Unknow and colors[i] != arrangement[i]:
                return False
        return True
    colors = self.actuators.color_sensors_read()
    if   check_arrangement(colors, [Color.Red, Color.Red, Color.Green, Color.Green]): reef_arrangement = 1
    elif check_arrangement(colors, [Color.Red, Color.Green, Color.Red, Color.Green]): reef_arrangement = 2
    elif check_arrangement(colors, [Color.Red, Color.Green, Color.Green, Color.Red]): reef_arrangement = 3

    # First set of reef buoys
    status = self.goth(theta=pi, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(status)
    status = self.goto_avoid(x=880, y=350, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(status)
    sleep(0.2)
    self.left_cup_holder_drop(use_queue=False)
    self.right_cup_holder_drop(use_queue=False)
    sleep(0.5)
    if reef_arrangement == 1:
        self.pumps_drop(ids='7,8', use_queue=False)
    else:
        self.pumps_drop(ids='7', use_queue=False)
        self.left_cup_holder_close(use_queue=False)
        sleep(0.5)
        rot = 2.75 if reef_arrangement == 2 else 2.45
        pump = '9' if reef_arrangement == 2 else '10'
        status = self.goth(theta=rot, use_queue=False)
        if status != RobotStatus.Reached:
            self.right_cup_holder_close(use_queue=False)
            return RobotStatus.return_status(status)
        sleep(0.2)
        self.pumps_drop(ids=pump, use_queue=False)
    status = self.move_trsl(40, 200, 200, 200, 1)
    self.left_cup_holder_close(use_queue=False)
    self.right_cup_holder_close(use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(status)

    # Second buoy of the front arm
    x=550
    status = self.goto_avoid(x=x, y=350, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(status)
    status = self.goth(theta=-pi/2, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(status)
    status = self.goto(x=x, y=250, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(status)
    sleep(0.2)
    self.pumps_drop(ids='4', use_queue=False)
    status = self.goto_avoid(x=x, y=350, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(status)

    # Second set of reef buoys
    status = self.goth(theta=pi, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(status)
    status = self.goto_avoid(x=325, y=350, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(status)
    self.left_cup_holder_drop(use_queue=False)
    self.right_cup_holder_drop(use_queue=False)
    rot = 0
    if reef_arrangement == 1: rot = 3*pi/4
    if reef_arrangement == 2: rot = 2.70
    if reef_arrangement == 3: rot = 2.70
    status = self.goth(theta=rot, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(status)
    sleep(0.2)
    pump = ''
    if reef_arrangement == 1: pump = '9,10'
    if reef_arrangement == 2: pump = '8'
    if reef_arrangement == 3: pump = '8,9'
    self.pumps_drop(ids=pump, use_queue=False)
    if reef_arrangement == 2:
        self.left_cup_holder_close(use_queue=False)
        sleep(0.5)
        status = self.goth(theta=3*pi/4, use_queue=False)
        if status != RobotStatus.Reached:
            self.right_cup_holder_close(use_queue=False)
            return RobotStatus.return_status(status)
        sleep(0.2)
        self.pumps_drop(ids='10', use_queue=False)
    status = self.move_trsl(40, 200, 200, 200, 1)
    self.left_cup_holder_close(use_queue=False)
    self.right_cup_holder_close(use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(status)

    status = self.goto_avoid(x=250, y=200, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(status)
    status = self.goth(theta=pi/2, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(status)
    status = self.goto(x=250, y=150, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(status)
    status = self.recal(0)
    if RobotStatus.get_status(status) != RobotStatus.NotReached: return RobotStatus.return_status(status)

    return RobotStatus.return_status(RobotStatus.Done)


