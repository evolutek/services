from evolutek.lib.map.tim import Tim
from time import sleep

def test_tim():

    config = {
        'min_size' : 4,
        'max_distance' : 45,
        'ip' : 'sick1',
        'port' : 2112,
        'pos_x' : 1000,
        'pos_y' : 3094,
        'angle' : 90,
        'delta_dist' : 40,
        'refresh' : 0.5,
        'window' : 5
    }

    print('[TEST_TIM] Starting TIM test')

    tim = Tim(config, False, False)

    sleep(0.5)

    if not tim.connected:
        print('[TEST_TIM] Failed to connect to TIM')
        return

    print('[TEST_TIM] Starting test')

    while True:
        robots = tim.get_scan()
        print('[TEST_TIM] New scan:')
        for robot in robots:
            print(robot)
        sleep(0.5)

if __name__ == '__main__':
    test_tim()
