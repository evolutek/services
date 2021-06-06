from evolutek.lib.map.tim import DebugMode, Tim
from time import sleep

def test_tim():

    computation_config = {
        'min_size' : 4,
        'max_distance' : 45,
        'delta_dist' : 40,
        'refresh' : 0.5,
        'radius_beacon': 40
    }

    config = {
        'ip' : 'sick3',
        'port' : 2111,
        'pos_x' : 1950,
        'pos_y' : 3094,
        'angle' : -90
    }

    print('[TEST_TIM] Starting TIM test')

    tim = Tim(config, config, True, False)

    sleep(0.5)

    if not tim.connected:
        print('[TEST_TIM] Failed to connect to TIM')
        return

    print('[TEST_TIM] Starting test')
    print('[TEST_TIM] estimated pos: %d, %d' % (tim.pos.x, tim.pos.y))

    while True:
        robots = tim.get_robots()
        print('[TEST_TIM] New scan:')
        for robot in robots:
            print(robot.to_dict())
        sleep(0.5)

if __name__ == '__main__':
    test_tim()
