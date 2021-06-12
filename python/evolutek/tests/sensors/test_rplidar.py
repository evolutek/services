from evolutek.utils.interfaces.rplidar_interface import RplidarInterface
from evolutek.lib.sensors.rplidar import Rplidar
from evolutek.lib.map.point import Point
from math import pi
from time import sleep
from threading import Thread
from cellaserv.service import AsynClient
from cellaserv.settings import get_socket

lidar = None
robot_position = Point(0, 0)
robot_theta = 0
ROBOT = 'pal' # Set to None to ignore telemetry

def start_interface():
    global lidar
    RplidarInterface(lidar)

def update_position(telemetry, **kwargs):
    global robot_position
    robot_position = Point(dict=telemetry)
    global robot_theta
    robot_theta = float(telemetry['theta'])
    #global lidar
    #lidar.set_position(Point(dict=telemetry), float(telemetry['theta']))

def test_lidar():
    global lidar

    config = {
        'max_distance' : 60,
        'min_size' : 3,
        'radius' : 40
    }

    print('[TEST_RPLIDAR] Starting lidar test')
    lidar = Rplidar(config)
    lidar.start_scanning()
    #lidar.set_position(Point(1000, 1500), pi)

    if ROBOT is not None:
        print('[TEST_RPLIDAR] Stating AsynClient')
        client = AsynClient(get_socket())
        client.add_subscribe_cb("%s_telemetry" % ROBOT, update_position)

    print('[TEST_RPLIDAR] Starting interface')
    Thread(target=start_interface).start()

    print('[TEST_RPLIDAR] Starting test')
    while True:
        robots = lidar.get_robots()
        print('[TEST_RPLIDAR] New scan:')
        print('Current robot position : %s' % str(robot_position))
        print('Current robot angle : %f' % robot_theta)
        for robot in robots:
            print('----------')
            print(robot)
            print(robot.change_referencial(robot_position, robot_theta))
            print('----------')
        sleep(0.5)

if __name__ == '__main__':
    test_lidar()
