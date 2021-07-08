from evolutek.lib.status import RobotStatus
from evolutek.lib.utils.wrappers import if_enabled, use_queue
from evolutek.lib.robot.robot_trajman import RecalSensor
from evolutek.lib.utils.color import Color
from evolutek.lib.settings import ROBOT

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

    speeds = self.trajman.get_speeds()
    self.trajman.set_trsl_max_speed(500)
    self.trajman.set_trsl_acc(300)
    self.trajman.set_trsl_dec(300)

    currentPos = self.trajman.get_position()
    # Top reefs
    if currentPos["theta"] > (- pi) / 4 and currentPos["theta"] < pi / 4:
        status = RobotStatus.get_status(self.goto_avoid(x = currentPos["x"] - 100, y = currentPos["y"], mirror=False, use_queue=False))
    # Bottom
    elif currentPos["theta"] > pi / 4 and currentPos["theta"] < 3 * pi / 4:
        status = RobotStatus.get_status(self.goto_avoid(x = currentPos["x"], y = currentPos["y"] - 100, mirror=False, use_queue=False))
    elif currentPos["theta"] < (-pi) / 4 and currentPos["theta"] > (- 3 * pi) / 4:
        status = RobotStatus.get_status(self.goto_avoid(x = currentPos["x"], y = currentPos["y"] + 100, mirror=False, use_queue=False))
    if status != RobotStatus.Reached:
        self.trajman.set_trsl_max_speed(speeds['trmax'])
        self.trajman.set_trsl_acc(speeds['tracc'])
        self.trajman.set_trsl_dec(speeds['trdec'])
        return RobotStatus.return_status(status)

    status = RobotStatus.get_status(self.homemade_recal(use_queue=False))
    if status == RobotStatus.Disabled or status == RobotStatus.Aborted:
        self.trajman.set_trsl_max_speed(speeds['trmax'])
        self.trajman.set_trsl_acc(speeds['tracc'])
        self.trajman.set_trsl_dec(speeds['trdec'])
        return RobotStatus.return_status(status)

    self.left_cup_holder_close(use_queue=False)
    self.right_cup_holder_close(use_queue=False)

    status = self.check_abort()
    if status != RobotStatus.Ok:
        self.trajman.set_trsl_max_speed(speeds['trmax'])
        self.trajman.set_trsl_acc(speeds['tracc'])
        self.trajman.set_trsl_dec(speeds['trdec'])
        return RobotStatus.return_status(status)

    sleep(0.25)


    status = RobotStatus.get_status(self.goto_avoid(x = currentPos["x"], y = currentPos["y"], mirror=False, use_queue=False))
    # status = RobotStatus.get_status(self.move_trsl(100, 300, 300, 300, 1))

    self.trajman.set_trsl_max_speed(speeds['trmax'])
    self.trajman.set_trsl_acc(speeds['tracc'])
    self.trajman.set_trsl_dec(speeds['trdec'])

    if status != RobotStatus.Reached:
        return RobotStatus.return_status(status)

    return RobotStatus.return_status(RobotStatus.Done)


@if_enabled
@use_queue
def start_lighthouse(self):

    speeds = self.trajman.get_speeds()
    self.trajman.set_trsl_max_speed(750)
    self.trajman.set_trsl_acc(300)
    self.trajman.set_trsl_dec(300)

    self.left_cup_holder_open(use_queue=False) if not self.side else self.right_cup_holder_open(use_queue=False)
    sleep(0.25)

    status = RobotStatus.get_status(self.goto_avoid(x=140, y=330, use_queue=False))
    if status != RobotStatus.Reached:
        self.left_cup_holder_close(use_queue=False) if not self.side else self.right_cup_holder_close(use_queue=False)
        self.trajman.set_trsl_max_speed(speeds['trmax'])
        self.trajman.set_trsl_acc(speeds['tracc'])
        self.trajman.set_trsl_dec(speeds['trdec'])
        return RobotStatus.return_status(status)

    status = RobotStatus.get_status(self.goto_avoid(x=300, y=330, use_queue=False))
    self.left_cup_holder_close(use_queue=False) if not self.side else self.right_cup_holder_close(use_queue=False)

    self.trajman.set_trsl_max_speed(speeds['trmax'])
    self.trajman.set_trsl_acc(speeds['tracc'])
    self.trajman.set_trsl_dec(speeds['trdec'])

    return RobotStatus.return_status(status if status != RobotStatus.Reached else RobotStatus.Done)


@if_enabled
@use_queue
def push_windsocks(self):

    status = RobotStatus.get_status(self.homemade_recal(decal=0, use_queue=False))
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
        print(f'[ROBOT] Adding {color.value} buoy to the score')
        if color not in [Color.Green, Color.Red]: return
        buoys_count[color] += 1
        score = calculate_score(buoys_count)
        print(f'[ROBOT] Score is now {score}')

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
        self.trajman.move_trsl(dest=50, acc=800, dec=800, maxspeed=1000, sens=0)
        self.pumps_drop(ids=pumps, use_queue=False, mirror=False)
        sleep(0.5)
        # Moves back
        status = self.goto_avoid(x=x, y=350, use_queue=False)
        if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(RobotStatus.get_status(status))
        return RobotStatus.return_status(RobotStatus.Done)

    def arm_buoy(x, pump, buoy, rot=False):
        nonlocal buoys_count
        nonlocal score
        # Moves forward to place the buoy
        status = self.goto_avoid(x=x, y=250, use_queue=False)
        if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(RobotStatus.get_status(status))
        if rot:
            status = self.goth(theta=(-1 if self.side else 1)*pi/2 + pi/6, mirror=False, use_queue=False)
            if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(RobotStatus.get_status(status))
        # Counts points
        prox, color = buoy
        if self.actuators.proximity_sensor_read(id=prox):
            update_buoys_count(color)
        # Drops the buoy
        self.trajman.move_trsl(dest=50, acc=800, dec=800, maxspeed=1000, sens=0)
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
            # Moves to the right y and lowers the arm
            status = self.goth(theta=pi/2, use_queue=False)
            if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(RobotStatus.get_status(status))
            if i <= 1: self.left_cup_holder_drop(use_queue=False)
            else: self.right_cup_holder_drop(use_queue=False)
            status = self.goto_avoid(x=x + x_offset, y=y, use_queue=False)
            if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(RobotStatus.get_status(status))
            # Drops, closes the arm and moves back
            self.trajman.move_trsl(dest=50, acc=800, dec=800, maxspeed=1000, sens=1)
            self.pumps_drop(ids=str(i+7), use_queue=False, mirror=False)
            update_buoys_count(color)
            if i <= 1: self.left_cup_holder_close(use_queue=False)
            else: self.right_cup_holder_close(use_queue=False)
            sleep(0.5)
            y += 120
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
    status = arm_buoy(x=1001 if self.side else 599, pump='1', buoy=(2, Color.Red), rot=True)
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
def goto_anchorage(self, time=None):

    # True == south
    # match_status = self.cs.match.get_status()
    # while match_status["time"] < 95:
    #     sleep(0.5)
    #     match_status = self.cs.match.get_status()
    anchorage = self.cs.match.get_anchorage() == "south"

    print(anchorage)

    current_y = float(self.trajman.get_position()['y'])
    x = 1350 if anchorage else 250
    status = self.goto_avoid(x=x, y=current_y, mirror=False, use_queue=False)

    if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(RobotStatus.get_status(status))

    status = self.goth(theta=pi/2, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return RobotStatus.return_status(RobotStatus.get_status(status))

    if time is not None:
        while float(time) > float(self.cs.match.get_status()['time']):
            sleep(0.5)

    status = self.goto(x=x, y=130 if ROBOT=='pmi' else 450, avoid=False, use_queue=False)

    if RobotStatus.get_status(status) not in [RobotStatus.Reached, RobotStatus.HasAvoid]:
        current_y = float(self.trajman.get_position()['y'])
        score = 10 if (current_y if self.side else 3000 - current_y) < 475 else 0
        return RobotStatus.return_status(RobotStatus.get_status(status), score=score)

   # if ROBOT == 'pmi':
        #status = self.homemade_recal(use_queue=False)
        #status = self.goto(x=130, )
        #if RobotStatus.get_status(status) not in [RobotStatus.Reached, RobotStatus.NotReached]:
         #   return RobotStatus.return_status(RobotStatus.get_status(status), score=10)

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
        if isinstance(color, list):
            for c in color:
                if c not in [Color.Green, Color.Red]: continue
                print(f'[ROBOT] Adding {c.value} buoy to the score')
                buoys_count[c] += 1
        else:
            
            if color not in [Color.Green, Color.Red]: return
            print(f'[ROBOT] Adding {color.value} buoy to the score')
            buoys_count[color] += 1
        score = calculate_score(buoys_count)
        print(f'[ROBOT] Score is now {score}')

    def check_front_buoys(buoys):
        for prox, color in buoys:
            if not self.side:
                color = Color.Green if color == Color.Red else Color.Red
            if self.actuators.proximity_sensor_read(id=prox):
                update_buoys_count(color)

    # Gets the first buoy in front of the zone
    self.pumps_get(ids=[5], use_queue=False)
    status = self.goth(theta=0, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return cleanup_and_exit(status)
    status = self.goto_avoid(x=1750, y=1705, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return cleanup_and_exit(status)

    # Recalibration on the central bar
    status = self.goth(theta=pi/2, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return cleanup_and_exit(status)
    status = self.recalibration(x=False, x_sensor=RecalSensor.Right, decal_y=1511, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Done: return cleanup_and_exit(status)

    # Gets the second buoy in front of the zone
    self.pumps_get(ids=[3], use_queue=False)    
    status = self.goto_avoid(x=1696, y=1700, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return cleanup_and_exit(status)
    status = self.goto_avoid(x=1696, y=1850, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return cleanup_and_exit(status)

    # Gets the first buoy on the back of the zone
    status = self.goto_avoid(x=1780, y=1800, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return cleanup_and_exit(status)
    status = self.goth(theta=0, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return cleanup_and_exit(status)
    self.pumps_get(ids=[2], use_queue=False)
    status = self.goto_avoid(x=1810, y=1680, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return cleanup_and_exit(status)

    # Gets the second buoy on the back of the zone
    status = self.goto_avoid(x=1780, y=1800, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return cleanup_and_exit(status)
    status = self.goth(theta=0, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return cleanup_and_exit(status)
    self.pumps_get(ids=[6], use_queue=False)
    status = self.goto_avoid(x=1810, y=1910, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return cleanup_and_exit(status)

    # Drops the 4 buoys on the front
    status = self.goto_avoid(x=1780, y=1800, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return cleanup_and_exit(status)
    status = self.goth(theta=0, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return cleanup_and_exit(status)
    status = self.goto_avoid(x=1810, y=1800, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return cleanup_and_exit(status)
    check_front_buoys([(1, Color.Red),(2, Color.Red),(3, Color.Green),(4, Color.Green)])
    sleep(0.1)
    self.trajman.move_trsl(dest=50, acc=1000, dec=1000, maxspeed=1000, sens=0)
    self.pumps_drop(ids=[2, 3, 5, 6], use_queue=False)

    # Gets into position to drop the front arm buoys
    status = self.goto_avoid(x=1700, y=1800, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return cleanup_and_exit(status)
    self.front_arm_open(use_queue=False)
    sleep(0.5)
    status = self.goto_avoid(x=1720, y=1800, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return cleanup_and_exit(status)

    # Drops the front arm buoys
    check_front_buoys([(2, Color.Red),(3, Color.Green)])
    sleep(0.1)
    self.trajman.move_trsl(dest=50, acc=1000, dec=1000, maxspeed=1000, sens=0)
    self.pumps_drop(ids=[1, 3, 4, 5], use_queue=False)
    status = self.goto_avoid(x=1500, y=1800, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return cleanup_and_exit(status)

    # Gets the color of all the reef buoy
    colors = self.actuators.color_sensors_read()
    colors = list(map(lambda c: Color.get_by_name(c), colors))
    print(f'[ROBOT] Read RGB sensors: {colors}')

    # Gets into position to drop the 2 exterior buoys on the back
    status = self.goth(theta=pi, mirror=False, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return cleanup_and_exit(status)
    self.left_cup_holder_drop(use_queue=False)
    self.right_cup_holder_drop(use_queue=False)
    status = self.goto_avoid(x=1620, y=1800, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return cleanup_and_exit(status)

    # Drops the 2 exterior buoys on the back
    update_buoys_count([colors[0], colors[3]])
    self.pumps_drop(ids=[7, 10], mirror=False, use_queue=False)
    self.left_cup_holder_close(use_queue=False)
    self.right_cup_holder_close(use_queue=False)
    sleep(0.5)

    # Drops the first central buoy
    status = self.goto_avoid(x=1550, y=1800, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return cleanup_and_exit(status)
    status = self.goth(theta= 3 * pi / 4, mirror=False, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return cleanup_and_exit(status)
    self.right_cup_holder_drop(use_queue=False)
    sleep(1)
    update_buoys_count([colors[2]])
    self.pumps_drop(ids=[9], mirror=False, use_queue=False)
    self.right_cup_holder_close(use_queue=False)
    sleep(0.5)

    # Drops the second central buoy
    status = self.goto_avoid(x=1550, y=1800, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return cleanup_and_exit(status)
    status = self.goth(theta= -2.5, mirror=False, use_queue=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached: return cleanup_and_exit(status)
    self.left_cup_holder_drop(use_queue=False)
    sleep(1)
    update_buoys_count([colors[1]])
    self.pumps_drop(ids=[8], mirror=False, use_queue=False)
    self.left_cup_holder_close(use_queue=False)
    sleep(0.5)

    return RobotStatus.return_status(RobotStatus.Done, score=score)
