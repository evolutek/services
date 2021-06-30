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
            if self.actuators.proximity_sensor_read(id=prox):
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
        if self.actuators.proximity_sensor_read(id=prox):
            update_buoys_count(color)
        # Drops the buoy
        self.trajman.move_trsl(dest=30, acc=100, dec=100, maxspeed=100, sens=0)
        self.pumps_drop(ids=pump, use_queue=False, mirror=False)
        sleep(0.5)
        # Moves back
        status = self.goto_avoid(x=x, y=350, use_queue=False)
        if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(RobotStatus.get_status(status), score=score)
        return RobotStatus.return_status(RobotStatus.Done)

    # The robot must be at 185mm from the center of the band
    def drop_theta(place, first):
        if not first: place -= 1
        if place == 0: return 0
        if place == 1: return 0.35
        if place == 2: return 0.75
        if place == 3: return 1.1

    def reef_buoys(theta, colors, color, multiplier=1):
        self.left_cup_holder_drop(use_queue=False)
        self.right_cup_holder_drop(use_queue=False)
        sleep(0.4)
        # Determines all the moves that must be done
        first = True
        buoys = [] # Stores a tuple for each buoy to place with (target theta, pump id)
        for i in range(4):
            if colors[i] == color:
                buoys.append((
                    drop_theta(i, first=first) * multiplier + theta,
                    str(i+7)
                ))
                first = False
        # Combines pump drops if possible
        if len(buoys) == 2 and buoys[0][0] == buoys[1][0]:
            buoys = [(buoys[0][0], buoys[0][1] + ',' + buoys[1][1])]
        # Does all the moves
        for th, pump in buoys:
            self.left_cup_holder_drop(use_queue=False)
            self.right_cup_holder_drop(use_queue=False)
            sleep(0.4)
            status = self.goth(theta=th, use_queue=False)
            if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(RobotStatus.get_status(status), score=score)
            self.pumps_drop(ids=pump, use_queue=False, mirror=False)
            update_buoys_count(color)
            if ',' in pump: update_buoys_count(color)
            self.left_cup_holder_close(use_queue=False)
            self.right_cup_holder_close(use_queue=False)
            sleep(0.4)
        return RobotStatus.return_status(RobotStatus.Done)

    status = self.recalibration(x=False, y=True, x_sensor=RecalSensor.Left, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Done: return RobotStatus.return_status(RobotStatus.get_status(status), score=score)

    # First set of front buoys
    print('[ROBOT] Dropping front green buoys')
    status = front_buoys(x=600 if self.side else 1010, pumps='5,6', buoys=[(3,Color.Green),(4,Color.Green)])
    if RobotStatus.get_status(status) != RobotStatus.Done: return RobotStatus.return_status(RobotStatus.get_status(status), score=score)

    # Second set of front buoys
    print('[ROBOT] Dropping front red buoys')
    status = front_buoys(x=1010 if self.side else 600, pumps='2,3', buoys=[(1,Color.Red),(2,Color.Red)])
    if RobotStatus.get_status(status) != RobotStatus.Done: return RobotStatus.return_status(RobotStatus.get_status(status), score=score)
    # First buoy of the front arm
    print('[ROBOT] Dropping front arm red buoys')
    self.front_arm_open(use_queue=False)
    sleep(0.5)
    status = arm_buoy(x=1010 if self.side else 600, pump='1', buoy=(2, Color.Red))
    if RobotStatus.get_status(status) != RobotStatus.Done: return RobotStatus.return_status(RobotStatus.get_status(status), score=score)

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
        status = self.goto_avoid(x=700, y=300, use_queue=False)
        if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(RobotStatus.get_status(status), score=score)
        status = reef_buoys(theta=0, colors=colors, color=Color.Red, multiplier= 1 if self.side else -1)
        if RobotStatus.get_status(status) != RobotStatus.Done: return RobotStatus.return_status(RobotStatus.get_status(status), score=score)

    # Second buoy of the front arm
    print('[ROBOT] Dropping front arm green buoys')
    x = 550 if self.side else 1030
    status = self.goto_avoid(x=x, y=300, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(RobotStatus.get_status(status), score=score)
    status = self.goth(theta=-pi/2, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(RobotStatus.get_status(status), score=score)
    status = arm_buoy(x=x, pump='4', buoy=(3, Color.Green))
    if RobotStatus.get_status(status) != RobotStatus.Done: return RobotStatus.return_status(RobotStatus.get_status(status), score=score)

    # Second set of reef buoys
    if Color.Green in colors:
        print('[ROBOT] Dropping reef green buoys')
        status = self.goto_avoid(x=900, y=300, use_queue=False)
        if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(RobotStatus.get_status(status), score=score)
        status = reef_buoys(theta=pi, colors=colors, color=Color.Green, multiplier= -1 if self.side else 1)
        if RobotStatus.get_status(status) != RobotStatus.Done: return RobotStatus.return_status(RobotStatus.get_status(status), score=score)

    return RobotStatus.return_status(RobotStatus.Done, score=score)


