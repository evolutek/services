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

def get_strat(color, actuators, robot):
    print('color')
    if color == 'green':
        if robot == 'pal':
            return get_strat_green_pal(actuators)
        else:
            return get_strat_green_pmi(actuators)
    else:
        if robot == 'pal':
            return get_strat_orange_pal(actuators)
        else:
            return get_strat_orange_pmi(actuators)

def get_strat_test():
    res = queue.Queue()
    res.put(Task(1000, 2240, not_avoid=True))
    for i in range(10000):
        res.put(Task(1700, 2240))
        res.put(Task(700, 2240))
    return res

def get_strat_test2():
    res = queue.Queue()
    for i in range(10000):
        res.put(Task(350, 2390))
        res.put(Task(1450, 2390))
        res.put(Task(1450, 610))
        res.put(Task(350, 610))
    return res

def homologation():
    res = queue.Queue()
    res.put(Task(750, 500))
    res.put(Task(150, 500))
    res.put(Task(150, 300))
    return res


def get_strat_orange_pal(actuators):
    res = queue.Queue()
    res.put(Task(1000, 2240, not_avoid=True))
    res.put(Task(1200, 2240))
    res.put(Task(1650, 2700))    
    res.put(Task(1650, 2760, theta=pi, func_ptr=actuators.open_arm, not_avoid=True))
    res.put(Task(1900, 2760, func_ptr=actuators.launch_bee, not_avoid=True))
    res.put(Task(1550, 2760, func_ptr=actuators.close_arm, not_avoid=True))
    res.put(Task(600,  2550))
    res.put(Task(350,  2550, not_avoid=True))
    res.put(Task(550,  2550, not_avoid=True))
    res.put(Task(815,  2550))
    res.put(Task(950,  2170))
    res.put(Task(600,  2150))
    res.put(Task(350,  2160, not_avoid=True))
    res.put(Task(450,  2160, not_avoid=True))
    res.put(Task(875,  2390, theta=-pi/2))
    res.put(Task(895,  2830, not_avoid=True, func_ptr=actuators.open_first_distrib))
    res.put(Task(895,  2600, not_avoid=True))
    res.put(Task(350, 1900))
    res.put(Task(350, 1920, theta=pi, func_ptr=actuators.open_arm2, not_avoid=True))
    res.put(Task(140, 1920, not_avoid=True, speed=200))
    return res

def get_strat_green_pal(actuators):
    res = queue.Queue()
    res.put(Task(1000, 760, not_avoid=True))
    res.put(Task(1200, 760))
    res.put(Task(1650, 300))    
    res.put(Task(1650, 190, theta=pi, func_ptr=actuators.open_arm, not_avoid=True))
    res.put(Task(1900, 190, func_ptr=actuators.launch_bee, not_avoid=True))
    res.put(Task(1550, 190, func_ptr=actuators.close_arm, not_avoid=True))
    res.put(Task(600,  500))
    res.put(Task(350,  500, not_avoid=True))
    res.put(Task(450,  450, not_avoid=True))
    res.put(Task(815,  450))
    res.put(Task(950,  830))
    res.put(Task(600,  850))
    res.put(Task(350,  840, not_avoid=True))
    res.put(Task(550,  840, not_avoid=True))
    res.put(Task(880,  610, theta=-pi/2))
    res.put(Task(870,  170, not_avoid=True, func_ptr=actuators.open_first_distrib))
    res.put(Task(870,  400, not_avoid=True))
    res.put(Task(350, 1150))
    res.put(Task(350, 1170, theta=pi, func_ptr=actuators.open_arm2, not_avoid=True))
    res.put(Task(140, 1170, not_avoid=True, speed=200))
    #res.put(Task(1200, 2400, theta=pi))
    #res.put(Task(1860, 2400, not_avoid=True, func_ptr=actuators.open_first_distrib))
    #res.put(Task(1600, 2400, not_avoid=True))
    return res

def get_strat_orange_pmi(actuators):
    res = queue.Queue()
    res.put(Task(250, 2720))
    res.put(Task(250, 1875, theta=pi, func_ptr=actuators.open_arm))
    res.put(Task(100, 1875, not_avoid=True, speed=200))
    res.put(Task(120, 1875, not_avoid=True, func_ptr=actuators.close_arm))
    return res

def get_strat_green_pmi(actuators):
    res = queue.Queue()
    res.put(Task(250, 280))
    res.put(Task(250, 1125, theta=pi, func_ptr=actuators.open_arm))
    res.put(Task(100, 1125, not_avoid=True, speed=200))
    res.put(Task(120, 1125, not_avoid=True, func_ptr=actuators.close_arm))
    return res

