# -*- coding: utf-8 -*-
"""
Created on Fri Mar 16 15:06:29 2018

@author: marko
"""

from math import pi
import queue

class Task:
    def __init__(self, x, y, theta = None, speed = None, func_ptr = None, func_param = None, not_avoid = False):
        self.x = x
        self.y = y
        self.theta = theta
        self.action = func_ptr
        self.action_param = func_param
        self.speed = speed
        self.not_avoid = not_avoid

def get_strat(color, actuators):
    if color == 'green':
        return get_strat_green(actuators)
    else:
        return get_strat_orange(actuators)

def get_strat_orange(actuators):  
    res = queue.Queue()
    res.put(Task(1200, 2240))
    res.put(Task(1650, 2700))#, func_ptr=actuators.open_bee_arm))
    #res.put(Task(1800, 2800, theta=pi/2))
    #res.put(Task(1800, 2550, func_ptr=actuators.close_bee_arm))
    #res.put(Task(1750, 2800))
    res.put(Task(600,  2550))
    res.put(Task(350,  2550, not_avoid=True))
    res.put(Task(815,  2600))
    res.put(Task(950,  2170, theta=pi/2))
    res.put(Task(600,  2150))
    res.put(Task(350,  2160, not_avoid=True))
    res.put(Task(350,  1930, theta=pi, not_avoid=True, func_ptr=actuators.move_arm, func_param=68))
    res.put(Task(240,  1930, not_avoid=True, speed=500))
    res.put(Task(245,  1930, not_avoid=True, func_ptr=actuators.move_arm, func_param=0, speed=500))
    return res

def get_strat_green(actuators):  
    res = queue.Queue()
    res.put(Task(1200, 760))
    res.put(Task(1650, 400))#, not_avoid=True, func_ptr=actuators.open_bee_arm))
    #res.put(Task(1800, 400, not_avoid=True, theta=-pi/2))
    #res.put(Task(1800, 550, not_avoid=True, func_ptr=actuators.close_bee_arm))
    #res.put(Task(1750, 400, not_avoid=True))
    res.put(Task(600,  450))
    res.put(Task(350,  450, not_avoid=True))
    res.put(Task(815,  400))
    res.put(Task(950,  830))
    res.put(Task(600,  850))
    res.put(Task(350,  840, not_avoid=True))
    res.put(Task(350,  1170, theta=pi, not_avoid=True, func_ptr=actuators.move_arm, func_param=68))
    res.put(Task(240,  1170, not_avoid=True, speed=500))
    res.put(Task(245,  1170, not_avoid=True, func_ptr=actuators.move_arm, func_param=0, speed=500))
    return res

def get_test():
    res = queue.Queue()
    res.put(Task(0, 1500, False, not_avoid=True))
    res.put(Task(0, 0, False, not_avoid=False))
    res.put(Task(0, 1500, False, not_avoid=True))
    return res
