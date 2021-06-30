from evolutek.lib.status import RobotStatus
from evolutek.lib.utils.wrappers import if_enabled, use_queue
from evolutek.lib.robot.robot_trajman import RecalSensor
from evolutek.lib.utils.color import Color

from time import sleep
from math import pi

def calculate_score(buoys):
    green = buoys[Color.Green]
    red = buoys[Color.Red]
    pairs = min(green, red)
    solo = green + red - pairs*2
    return solo*2 + pairs*6

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

    status = RobotStatus.get_status(self.move_trsl(100, 300, 300, 300, 0))
    if status != RobotStatus.Reached:
        return RobotStatus.return_status(status)

    status = RobotStatus.get_status(self.recal(0))
    if status == RobotStatus.Disabled or status == RobotStatus.Aborted:
        return RobotStatus.return_status(status)

    self.left_cup_holder_close(use_queue=False)
    self.right_cup_holder_close(use_queue=False)

    status = self.check_abort()
    if status != RobotStatus.Ok:
        return RobotStatus.return_status(RobotStatus.get_status(status))

    sleep(0.25)

    status = RobotStatus.get_status(self.move_trsl(100, 300, 300, 300, 1))
    if status != RobotStatus.Reached:
        return RobotStatus.return_status(RobotStatus.get_status(status))

    return RobotStatus.return_status(RobotStatus.Done)


@if_enabled
@use_queue
def start_lighthouse(self):

    self.left_cup_holder_open(use_queue=False) if not self.side else self.right_cup_holder_open(use_queue=False)
    sleep(0.25)

    status = RobotStatus.get_status(self.goto_avoid(x=170, y=330, use_queue=False))
    if status != RobotStatus.Reached:
        self.left_cup_holder_close(use_queue=False) if not self.side else self.right_cup_holder_close(use_queue=False)
        return RobotStatus.return_status(status)

    status = RobotStatus.get_status(self.goto_avoid(x=300, y=330, use_queue=False))
    self.left_cup_holder_close(use_queue=False) if not self.side else self.right_cup_holder_close(use_queue=False)

    return RobotStatus.return_status(status if status != RobotStatus.Reached else RobotStatus.Done)


@if_enabled
@use_queue
def push_windsocks(self):

    status = RobotStatus.get_status(self.recal(0))
    if status == RobotStatus.Disabled or status == RobotStatus.Aborted:
        return RobotStatus.return_status(status)

    self.right_arm_open(use_queue=False) if self.side else self.left_arm_open(use_queue=False)

    sleep(1)

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
        return RobotStatus.return_status(RobotStatus.get_status(status))

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

    status = RobotStatus.get_status(self.goto_avoid(x=1825, y=650, use_queue=False))
    if status != RobotStatus.Reached:
        return RobotStatus.return_status(status)

    return RobotStatus.return_status(RobotStatus.Done)


@if_enabled
@use_queue
def drop_start_sorting(self):

    # TODO Handle both sides

    # Start position: 200 400 pi/2

    buoys_count = {
        Color.Green: 0,
        Color.Red: 0,
    }
    score = 0

    def update_buoys_count(color):
        nonlocal buoys_count
        nonlocal score
        if color not in [Color.Green, Color.Red]: return
        buoys_count[color] += 1
        score = calculate_score(buoys_count)

    def front_buoys(x, pumps, buoys):
        nonlocal buoys_count
        nonlocal score
        # Gets into position
        status = self.goto_avoid(x=x, y=250, use_queue=False)
        if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(RobotStatus.get_status(status), score=score)
        status = self.goth(theta=-pi/2, use_queue=False)
        if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(RobotStatus.get_status(status), score=score)
        # Moves forward to place buoys
        status = self.goto_avoid(x=x, y=180, use_queue=False)
        if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(RobotStatus.get_status(status), score=score)
        sleep(0.2)
        # Counts points
        for prox, color in buoys:
            if self.actuators.proximity_sensor_read(id=prox, mirror=False):
                update_buoys_count(color)
        # Drops the buoys
        self.trajman.move_trsl(dest=30, acc=100, dec=100, maxspeed=100, sens=0)
        self.pumps_drop(ids=pumps, use_queue=False, mirror=False)
        sleep(0.5)
        # Moves back
        status = self.goto_avoid(x=x, y=350, use_queue=False)
        if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(RobotStatus.get_status(status), score=score)
        return RobotStatus.return_status(RobotStatus.Done)

    def arm_buoy(x, pump, buoy):
        nonlocal buoys_count
        nonlocal score
        # Moves forward to place the buoy
        status = self.goto_avoid(x=x, y=250, use_queue=False)
        if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(RobotStatus.get_status(status), score=score)
        sleep(0.2)
        # Counts points
        prox, color = buoy
        if self.actuators.proximity_sensor_read(id=prox, mirror=False):
            update_buoys_count(color)
        # Drops the buoy
        self.trajman.move_trsl(dest=30, acc=100, dec=100, maxspeed=100, sens=0)
        self.pumps_drop(ids=pump, use_queue=False, mirror=False)
        sleep(0.5)
        # Moves back
        status = self.goto_avoid(x=x, y=350, use_queue=False)
        if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(RobotStatus.get_status(status), score=score)
        return RobotStatus.return_status(RobotStatus.Done)

    status = self.recalibration(x=False, y=True, x_sensor=RecalSensor.Left, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Done: return RobotStatus.return_status(RobotStatus.get_status(status), score=score)

    # First set of front buoys
    status = front_buoys(x=600 if self.side else 1010, pumps='5,6', buoys=[(3,Color.Green),(4,Color.Green)])
    if RobotStatus.get_status(status) != RobotStatus.Done: return RobotStatus.return_status(RobotStatus.get_status(status), score=score)

    # Second set of front buoys
    status = front_buoys(x=1010 if self.side else 600, pumps='2,3', buoys=[(1,Color.Red),(2,Color.Red)])
    if RobotStatus.get_status(status) != RobotStatus.Done: return RobotStatus.return_status(RobotStatus.get_status(status), score=score)
    # First buoy of the front arm
    self.front_arm_open(use_queue=False)
    sleep(0.5)
    status = arm_buoy(x=1010 if self.side else 600, pump='1', buoy=(2, Color.Red))
    if RobotStatus.get_status(status) != RobotStatus.Done: return RobotStatus.return_status(RobotStatus.get_status(status), score=score)

    # Possible arrangements on blue side
    # 1: R R G G
    # 2: R G R G
    # 3: R G G R
    reef_arrangement = 0
    def check_arrangement(colors, arrangement):
        for i in range(4):
            if colors[i] == Color.Unknown: continue
            if (colors[i] != arrangement[i]) ^ self.side:
                return False
        return True
    colors = self.actuators.color_sensors_read()
    colors = list(map(lambda c: Color.get_by_name(c), colors))
    print(f'[ROBOT] Read RGB sensors: {colors}')
    if not Color.Red in colors and not Color.Green in colors: reef_arrangement = 0
    elif check_arrangement(colors, [Color.Red, Color.Red, Color.Green, Color.Green]): reef_arrangement = 1
    elif check_arrangement(colors, [Color.Red, Color.Green, Color.Red, Color.Green]): reef_arrangement = 2
    elif check_arrangement(colors, [Color.Red, Color.Green, Color.Green, Color.Red]): reef_arrangement = 3
    print(f'[ROBOT] reef_arrangement={reef_arrangement}')

    # First set of reef buoys
    if reef_arrangement != 0:
        status = self.goth(theta=pi, use_queue=False)
        if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(RobotStatus.get_status(status), score=score)
        status = self.goto_avoid(x=880, y=350, use_queue=False)
        if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(RobotStatus.get_status(status), score=score)
        sleep(0.2)
        self.left_cup_holder_drop(use_queue=False)
        self.right_cup_holder_drop(use_queue=False)
        sleep(0.5)
        if reef_arrangement == 1:
            self.pumps_drop(ids='7,8', use_queue=False, mirror=False)
            update_buoys_count(colors[0])
            update_buoys_count(colors[1])
        else:
            self.pumps_drop(ids='7', use_queue=False, mirror=False)
            update_buoys_count(colors[0])
            self.left_cup_holder_close(use_queue=False)
            sleep(0.5)
            rot = 2.75 if reef_arrangement == 2 else 2.45
            pump = '9' if reef_arrangement == 2 else '10'
            status = self.goth(theta=rot, use_queue=False)
            if RobotStatus.get_status(status) != RobotStatus.Reached:
                self.right_cup_holder_close(use_queue=False)
                return RobotStatus.return_status(RobotStatus.get_status(status), score=score)
            sleep(0.2)
            self.pumps_drop(ids=pump, use_queue=False, mirror=False)
            update_buoys_count(colors[2 if reef_arrangement == 2 else 3])
        status = self.move_trsl(40, 200, 200, 200, 1)
        self.left_cup_holder_close(use_queue=False)
        self.right_cup_holder_close(use_queue=False)
        if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(RobotStatus.get_status(status), score=score)

    # Second buoy of the front arm
    x=550 if self.side else 1030
    status = self.goto_avoid(x=x, y=350, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(RobotStatus.get_status(status), score=score)
    status = self.goth(theta=-pi/2, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(RobotStatus.get_status(status), score=score)
    status = arm_buoy(x=x, pump='4', buoy=(3, Color.Green))
    if RobotStatus.get_status(status) != RobotStatus.Done: return RobotStatus.return_status(RobotStatus.get_status(status), score=score)

    # Second set of reef buoys
    if reef_arrangement != 0:
        status = self.goth(theta=pi, use_queue=False)
        if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(RobotStatus.get_status(status), score=score)
        status = self.goto_avoid(x=325, y=350, use_queue=False)
        if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(RobotStatus.get_status(status), score=score)
        self.left_cup_holder_drop(use_queue=False)
        self.right_cup_holder_drop(use_queue=False)
        rot = 0
        if reef_arrangement == 1: rot = 3*pi/4
        if reef_arrangement == 2: rot = 2.70
        if reef_arrangement == 3: rot = 2.70
        status = self.goth(theta=rot, use_queue=False)
        if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(RobotStatus.get_status(status), score=score)
        sleep(0.2)
        pump = ''
        if reef_arrangement == 1:
            pump = '9,10'
            update_buoys_count(colors[2])
            update_buoys_count(colors[3])
        if reef_arrangement == 2:
            pump = '8'
            update_buoys_count(colors[1])
        if reef_arrangement == 3:
            pump = '8,9'
            update_buoys_count(colors[1])
            update_buoys_count(colors[2])
        self.pumps_drop(ids=pump, use_queue=False, mirror=False)
        if reef_arrangement == 2:
            self.left_cup_holder_close(use_queue=False)
            sleep(0.5)
            status = self.goth(theta=3*pi/4, use_queue=False)
            if RobotStatus.get_status(status) != RobotStatus.Reached:
                self.right_cup_holder_close(use_queue=False)
                return RobotStatus.return_status(RobotStatus.get_status(status), score=score)
            sleep(0.2)
            self.pumps_drop(ids='10', use_queue=False, mirror=False)
            update_buoys_count(colors[3])
        status = self.move_trsl(40, 200, 200, 200, 1)
        self.left_cup_holder_close(use_queue=False)
        self.right_cup_holder_close(use_queue=False)
        if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(RobotStatus.get_status(status), score=score)

    return RobotStatus.return_status(RobotStatus.Done, score=score)


