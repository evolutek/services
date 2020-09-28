#!/usr/bin/python3

from threading import Thread, Event, Lock
from time import sleep, time

from cellaserv.proxy import CellaservProxy

from evolutek.utils.map_interface import MapInterface
from evolutek.lib.map.map import Map, ObstacleType, parse_obstacle_file
from evolutek.lib.map.point import Point
from evolutek.lib.map.tim import DebugMode
from evolutek.lib.map.utils import convert_path_to_dict

class Test_Map:

    def __init__(self):

        self.cs = CellaservProxy()

        # Threads
        Thread(target=MapInterface).start()
        Thread(target=self.fake_robot).start()
        Thread(target=self.loop_path).start()

    def loop_path(self):
        sleep(2) # Ensures that the interface has started
        while True:
            print('[TEST_MAP] Update path')
            start = time()
            self.cs.map.get_path(
                    origin={'x':250,'y':500},
                    dest={'x':1700,'y':1800},
                    robot='pal')
            end = time()
            print('Path compute in: ' + str(end-start))

    def fake_robot(self):
        # TODO
        pass

if __name__ == "__main__":
    print('[TEST_MAP] Starting test')
    test_map = Test_Map()
