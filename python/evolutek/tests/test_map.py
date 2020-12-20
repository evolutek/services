#!/usr/bin/python3

from threading import Thread, Event, Lock
from time import sleep, time

from cellaserv.proxy import CellaservProxy

from evolutek.utils.map_interface import MapInterface

class Test_Map:

    def __init__(self):

        self.cs = CellaservProxy()

        # Threads
        Thread(target=MapInterface).start()
        Thread(target=self.loop_path).start()


    def loop_path(self):

        sleep(1) # Ensures that the interface has started

        right = True
        y = 500
        speed = 50
        bounds = (500, 2500)

        while True:

            sleep(0.1)

            y += speed if right else -speed
            if y > bounds[1]:
                y = bounds[1]
                right = False
            if y < bounds[0]:
                y = bounds[0]
                right = True

            print('[TEST_MAP] Update path')
            start = time()
            self.cs.map.get_path(
                    origin={'x':250,'y':y},
                    dest={'x':1700,'y':1800},
                    robot='pal')
            end = time()
            print('Path computed in: ' + str(end-start))

if __name__ == "__main__":
    print('[TEST_MAP] Starting test')
    test_map = Test_Map()
