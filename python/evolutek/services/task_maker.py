# -*- coding: utf-8 -*-
"""
Created on Fri Mar 16 15:06:29 2018

@author: marko
"""

from math import pi
import queue

class Task:
    def __init__(self, x, y, is_green, theta = None, speed = None, func_ptr = None, not_avoid = False):
        self.x = x
        if (is_green):
            y = 3000 - y
        self.y = y
        if (theta and is_green):
            theta = -theta
        self.theta = theta
        self.action = func_ptr
        self.speed = speed
        self.not_avoid = not_avoid



def get_strat(is_green = False):
    res = queue.Queue()
    res.put(Task(1200, 2240, is_green))
    res.put(Task(1650, 2700, is_green))
    res.put(Task(1800, 2700, is_green))
    res.put(Task(600,  2550, is_green))
    res.put(Task(350,  2550, is_green, not_avoid=True))
    res.put(Task(815,  2600, is_green, theta=pi/2))
    res.put(Task(815,  2700, is_green, not_avoid=True))
    res.put(Task(950,  2170, is_green, theta=pi/2))
    res.put(Task(815,  2150, is_green))
    res.put(Task(350,  2160, is_green))
    res.put(Task(350,  1970, is_green, theta=pi))
    res.put(Task(200,  1960, is_green, not_avoid=True))
    return res

def get_test():
    res = queue.Queue()
    res.put(Task(0, 1500, False))
    res.put(Task(0, 0, False))
    return res
