#!/usr/bin/env python3
from evolutek.lib.debug_map import Interface
from evolutek.lib.map import ObstacleType, Map as Map_lib
from evolutek.lib.point import Point

from time import *

from threading import Thread
width = 3000
height = 2000
map_unit = 25

def thread_path(self):
    while True:
        self.path = self.Map.get_path(Point(1650, 225), Point(1650, 2775))
        sleep(0.15)

def fake_robot(self):
        robot = {'x': 250, 'y': 1500}
        ascending = True
        while True:
            if ascending:
                robot['x'] += 10
                if robot['x'] > 1750:
                    robot['x'] = 1749
                    ascending = False
            else:
                robot['x'] -= 10
                if robot['x'] < 250:
                    robot['x'] = 251
                    ascending = True

            self.Map.remove_obstacle('fake')
            self.Map.add_circle_obstacle(robot['x'], robot['y'], self.robot_size, tag='fake', type=ObstacleType.robot)

            sleep(0.15)
    

class test:

    def __init__(self):
        self.pal_size = 150
        self.Map = Map_lib(width, height, map_unit, self.pal_size)
        """ Add obstacles """
        self.Map.add_rectangle_obstacle(1622, 2000, 450, 2550)
        self.Map.add_rectangle_obstacle(1422, 1622, 1475, 1525)
        self.Map.add_rectangle_obstacle(0, 50, 500, 2500)

        #self.Map.add_circle_obstacle(1000, 1500, 150, "robot", ObstacleType.robot)
        print("map_init : done")
        # Example
        self.path =  self.Map.get_path(Point(1000, 225), Point(1000,2500))
        print("path     : done")
        #print(self.path)
        self.debug = False
        self.robot_size = 150
        self.pal_telem = {'x': 1000, 'y': 1500, 'theta': 0}

        self.robots = []

        #Thread(target=Interface, args=[self.Map, self]).start()
        self.path = self.Map.get_path(Point(1650, 225), Point(1650, 2775))

        
        print("path refrech")
        thread_p = Thread(target=thread_path, args=(self, ))
        thread_p.start()
        thread_robo = Thread(target=fake_robot, args=(self, ))
        thread_robo.start()
        #thread = Thread(target=Interface, args=(self.Map, self, ))
        #thread.start()
        Interface(self.Map,self)
        


        


if __name__ == "__main__":
    t = test()
    while True:
        pass

