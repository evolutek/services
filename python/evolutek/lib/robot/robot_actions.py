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
def drop_start(self):

    # Start position: 200 400 pi/2

    buoys_count = {
        Color.Green: 0,
        Color.Red: 0,
    }
    score = 0

    speeds = self.trajman.get_speeds()
    self.trajman.set_trsl_max_speed(1000)
    self.trajman.set_trsl_acc(600)
    self.trajman.set_trsl_dec(600)

    def cleanup_and_exit(status):
        nonlocal speeds
        nonlocal score
        self.trajman.set_trsl_max_speed(speeds['trmax'])
        self.trajman.set_trsl_acc(speeds['tracc'])
        self.trajman.set_trsl_dec(speeds['trdec'])
        return RobotStatus.return_status(RobotStatus.get_status(status), score=score)

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
        if RobotStatus.get_status(status) != RobotStatus.Reached: return
        status = self.goth(theta=-pi/2, use_queue=False)
        if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(RobotStatus.get_status(status))
        # Moves forward to place buoys
        status = self.goto_avoid(x=x, y=180, use_queue=False)
        if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(RobotStatus.get_status(status))
        sleep(0.2)
        # Counts points
        for prox, color in buoys:
            if self.actuators.proximity_sensor_read(id=prox):
                update_buoys_count(color)
        # Drops the buoys
        self.trajman.move_trsl(dest=50, acc=1000, dec=1000, maxspeed=1000, sens=0)
        self.pumps_drop(ids=pumps, use_queue=False, mirror=False)
        sleep(0.5)
        # Moves back
        status = self.goto_avoid(x=x, y=350, use_queue=False)
        if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(RobotStatus.get_status(status))
        return RobotStatus.return_status(RobotStatus.Done)

    def arm_buoy(x, pump, buoy):
        nonlocal buoys_count
        nonlocal score
        # Moves forward to place the buoy
        status = self.goto_avoid(x=x, y=250, use_queue=False)
        if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(RobotStatus.get_status(status))
        sleep(0.2)
        # Counts points
        prox, color = buoy
        if self.actuators.proximity_sensor_read(id=prox):
            update_buoys_count(color)
        # Drops the buoy
        self.trajman.move_trsl(dest=50, acc=1000, dec=1000, maxspeed=1000, sens=0)
        self.pumps_drop(ids=pump, use_queue=False, mirror=False)
        sleep(0.5)
        # Moves back
        status = self.goto_avoid(x=x, y=350, use_queue=False)
        if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(RobotStatus.get_status(status))
        return RobotStatus.return_status(RobotStatus.Done)

    def reef_buoys(x, colors, color):
        y = 400
        for i in range(4):
            if colors[i] != color: continue
            # Moves to the right x
            x_offset = (i*75 - 109.5) * (-1 if self.side else 1)
            status = self.goto_avoid(x=x + x_offset, y=y + 100, use_queue=False)
            if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(RobotStatus.get_status(status))
            # Opens the arm
            if i <= 1: self.left_cup_holder_drop(use_queue=False)
            else: self.right_cup_holder_drop(use_queue=False)
            status = self.goth(theta=pi/2, use_queue=False)
            if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(RobotStatus.get_status(status))
            sleep(0.4)
            # Moves to the right y
            status = self.goto_avoid(x=x + x_offset, y=y, use_queue=False)
            if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(RobotStatus.get_status(status))
            # Closes the arm and moves back
            self.trajman.move_trsl(dest=50, acc=1000, dec=1000, maxspeed=1000, sens=1)
            self.pumps_drop(ids=str(i+7), use_queue=False, mirror=False)
            update_buoys_count(color)
            if i <= 1: self.left_cup_holder_close(use_queue=False)
            else: self.right_cup_holder_close(use_queue=False)
            sleep(0.5)
            y += 80
        return RobotStatus.return_status(RobotStatus.Done)

    status = self.recalibration(x=False, y=True, x_sensor=RecalSensor.Left, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Done: return cleanup_and_exit(status)

    # First set of front buoys
    print('[ROBOT] Dropping front green buoys')
    status = front_buoys(x=599 if self.side else 1001, pumps='5,6', buoys=[(3,Color.Green),(4,Color.Green)])
    if RobotStatus.get_status(status) != RobotStatus.Done: return cleanup_and_exit(status)

    # Second set of front buoys
    print('[ROBOT] Dropping front red buoys')
    status = front_buoys(x=1001 if self.side else 599, pumps='2,3', buoys=[(1,Color.Red),(2,Color.Red)])
    if RobotStatus.get_status(status) != RobotStatus.Done: return cleanup_and_exit(status)
    # First buoy of the front arm
    print('[ROBOT] Dropping front arm red buoys')
    self.front_arm_open(use_queue=False)
    sleep(0.5)
    status = arm_buoy(x=1001 if self.side else 599, pump='1', buoy=(2, Color.Red))
    if RobotStatus.get_status(status) != RobotStatus.Done: return cleanup_and_exit(status)

    #       Possible arrangements
    #  Blue side            Yellow side
    # 1: R R G G            1: G G R R
    # 2: R G R G            2: G R G R
    # 3: R G G R            3: G R R G
    colors = self.actuators.color_sensors_read()
    colors = list(map(lambda c: Color.get_by_name(c), colors))
    print(f'[ROBOT] Read RGB sensors: {colors}')

    # First set of reef buoys
    if Color.Red in colors:
        print('[ROBOT] Dropping reef red buoys')
        status = reef_buoys(x= 1085 if self.side else 515, colors=colors, color=Color.Red)
        if RobotStatus.get_status(status) != RobotStatus.Done: return cleanup_and_exit(status)

    # Second buoy of the front arm
    print('[ROBOT] Dropping front arm green buoys')
    x = 556 if self.side else 1044
    status = self.goto_avoid(x=x, y=300, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return cleanup_and_exit(status)
    status = self.goth(theta=-pi/2, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return cleanup_and_exit(status)
    status = arm_buoy(x=x, pump='4', buoy=(3, Color.Green))
    if RobotStatus.get_status(status) != RobotStatus.Done: return cleanup_and_exit(status)

    # Second set of reef buoys
    if Color.Green in colors:
        print('[ROBOT] Dropping reef green buoys')
        status = reef_buoys(x= 515 if self.side else 1085, colors=colors, color=Color.Green)
        if RobotStatus.get_status(status) != RobotStatus.Done: return cleanup_and_exit(status)

    self.trajman.set_trsl_max_speed(speeds['trmax'])
    self.trajman.set_trsl_acc(speeds['tracc'])
    self.trajman.set_trsl_dec(speeds['trdec'])

    return RobotStatus.return_status(RobotStatus.Done, score=score)


@if_enabled
@use_queue
def goto_anchorage(self):

    # True == south
    anchorage = self.cs.match.get_anchorage() == "south"

    x = 1350 if anchorage else 250
    status = self.goto_avoid(x=x, y=700, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(RobotStatus.get_status(status))
    status = self.goth(theta=pi/2, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(RobotStatus.get_status(status))

    speeds = self.trajman.get_speeds()
    self.trajman.set_trsl_max_speed(1000)
    self.trajman.set_trsl_acc(600)
    self.trajman.set_trsl_dec(600)

    status = self.goto(x=x, y=150, use_queue=False)

    self.trajman.set_trsl_max_speed(speeds['trmax'])
    self.trajman.set_trsl_acc(speeds['tracc'])
    self.trajman.set_trsl_dec(speeds['trdec'])

    if RobotStatus.get_status(status) not in [RobotStatus.Reached, RobotStatus.HasAvoid]:
        score = 10 if self.trajman.get_position()['y'] < 475 else 0
        return RobotStatus.return_status(RobotStatus.get_status(status), score=score)

    status = self.recal(0)
    if RobotStatus.get_status(status) not in [RobotStatus.Reached, RobotStatus.NotReached]:
        return RobotStatus.return_status(RobotStatus.get_status(status), score=10)

    return RobotStatus.return_status(RobotStatus.Done, score=10)

@if_enabled
@use_queue
def drop_center(self):

    # Starting pos: 1400 1705 theta=0

    buoys_count = {
        Color.Green: 0,
        Color.Red: 0,
    }
    score = 0

    speeds = self.trajman.get_speeds()
    self.trajman.set_trsl_max_speed(1000)
    self.trajman.set_trsl_acc(600)
    self.trajman.set_trsl_dec(600)

    def cleanup_and_exit(status):
        nonlocal speeds
        nonlocal score
        self.trajman.set_trsl_max_speed(speeds['trmax'])
        self.trajman.set_trsl_acc(speeds['tracc'])
        self.trajman.set_trsl_dec(speeds['trdec'])
        return RobotStatus.return_status(RobotStatus.get_status(status), score=score)

    def update_buoys_count(color):
        nonlocal buoys_count
        nonlocal score
        if color not in [Color.Green, Color.Red]: return
        buoys_count[color] += 1
        score = calculate_score(buoys_count)

    # Gets the first buoy in front of the zone
    self.pumps_drop(ids=[5], use_queue=False)
    status = self.goto_avoid(x=1750, y=1705, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return cleanup_and_exit(status)

    # Recalibration on the central bar
    status = self.goth(theta=pi/2, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return cleanup_and_exit(status)
    status = self.recalibration(x=False, x_sensor=RecalSensor.Right, decal_y=1511, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Done: return cleanup_and_exit(status)

    # Gets the second buoy in front of the zone
    self.pumps_get(ids=[3], use_queue=False)
    status = self.goto_avoid(x=1720, y=1855, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return cleanup_and_exit(status)
    status = self.goto_avoid(x=1780, y=1800, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return cleanup_and_exit(status)
    status = self.goth(theta=0, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return cleanup_and_exit(status)
    self.pumps_get(ids=[2], use_queue=False)
    status = self.goto_avoid(x=1810, y=1680, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return cleanup_and_exit(status)
    status = self.goto_avoid(x=1780, y=1800, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return cleanup_and_exit(status)    
    self.pumps_get(ids=[6], use_queue=False)
    status = self.goto_avoid(x=1810, y=1910, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return cleanup_and_exit(status)
    status = self.goto_avoid(x=1780, y=1800, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return cleanup_and_exit(status)
    status = self.goth(theta=0, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return cleanup_and_exit(status)
    status = self.goto_avoid(x=1810, y=1800, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return cleanup_and_exit(status)
    self.trajman.move_trsl(dest=50, acc=1000, dec=1000, maxspeed=1000, sens=0)
    self.pumps_drop(ids=[2, 3, 5, 6])
    status = self.goto_avoid(x=1700, y=1800, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return cleanup_and_exit(status)
    self.front_arm_open()
    status = self.goto_avoid(x=1720, y=1800, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return cleanup_and_exit(status)
    self.pumps_drop(ids=[1, 3, 4, 5])
    sleep(1)
    status = self.goto_avoid(x=1500, y=1800, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return cleanup_and_exit(status)
    status = self.goth(theta=pi)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return cleanup_and_exit(status)
    self.left_cup_holder_drop()
    self.right_cup_holder_drop()
    status = self.goto_avoid(x=1620, y=1800, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return cleanup_and_exit(status)
    self.pumps_drop(ids=[7, 10])
    status = self.goto_avoid(x=1580, y=1800, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return cleanup_and_exit(status)
    status = self.goth(theta= 3 * pi / 4, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return cleanup_and_exit(status)
    self.pumps_drop(ids=[9])
    self.left_cup_holder_close()
    self.right_cup_holder_close()
    status = self.goto_avoid(x=1540, y=1800, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return cleanup_and_exit(status)
    status = self.goth(theta= -3 * pi / 4, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return cleanup_and_exit(status)
    self.left_cup_holder_drop()
    self.pumps_drop(ids=[8])
    self.left_cup_holder_close()
    status = self.goth(theta=pi, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return cleanup_and_exit(status)



"""
robot.pumps_get(ids=[3]) done
robot.goto(1720, 1855) done
input()

robot.goto(1780, 1800) done
robot.goth(0) done
input()

robot.pumps_get(ids=[2]) done
robot.goto(1810, 1680) done
input()

robot.goto(1780, 1800) done
robot.goth(0)
input()

robot.pumps_get(ids=[6]) done
robot.goto(1810, 1910) done
input()

robot.goto(1780, 1800) done
robot.goth(0) done
input()

robot.goto(1810, 1800) done
input()

trajman.move_trsl(dest=50, acc=1000, dec=1000, maxspeed=1000, sens=0) done
robot.pumps_drop(ids=[2, 3, 5, 6]) done
robot.goto(1700, 1800) done
input()

robot.front_arm_open() done
robot.goto(1720, 1800) done
input()

robot.pumps_drop(ids=[1, 3, 4, 5]) done
sleep(1) done
robot.goto(1500, 1800) done
input()

robot.goth(pi) done
robot.left_cup_holder_drop() done
robot.right_cup_holder_drop() done
input()

robot.goto(1620, 1800) done
input()

robot.pumps_drop(ids=[7, 10]) done
robot.goto(1580, 1800) done
input()

robot.goth(3*pi/4) done
input()

robot.pumps_drop(ids=[9]) done
robot.left_cup_holder_close() done
robot.right_cup_holder_close() done
input()

robot.goto(1540, 1800) done
robot.goth(-3*pi/4) done
robot.left_cup_holder_drop() done
input()

robot.pumps_drop(ids=[8]) done
robot.left_cup_holder_close() done
input()

robot.goth(pi) done
input() 
"""
