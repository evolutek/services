# -*- coding: utf-8 -*-
"""
Created on Fri Mar 16 15:06:29 2018

@author: marko
"""

from math import pi
import queue

path = [  # orange side                 \
         (1200, 2240, None),            \
         (1650, 2700, 0),               \
         (1800, 2700, 0),               \
         (350,  2550, pi/2), # push bee \
         (815,  2600, pi/2),            \
         (815,  2600, pi/2),            \
         (950,  2170, pi/2), # maybe this point is irrelevant \
         (815,  2150, None), # maybe set a theta value        \
         (350,  2160, None), # maybe set a theta value        \
         (350,  1970, None), # maybe set a theta value        \
         (130,  1960, None)  # maybe set a theta value        \
       ]


class Task:
    def __init__(self, x, y, theta = None, speed = None, func_ptr = None, not_avoid = False, is_green = False):
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
    for x in path:
        res.put(Task(x[0], x[1], theta = x[2], is_green = is_green))
    return res
