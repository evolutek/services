# -*- coding: utf-8 -*-
"""
Created on Fri Mar 16 15:06:29 2018

@author: marko
"""

from math import pi
import queue

class Task:
    """
    Class Task which represent a movement and the associated action:
    x, y : coordinates
    theta : rotation at the end
    func_ptr : the action to do (pointeur on function)
    func_param: list of parameters
    speed: the speed
    not_avoid: boolean which says if the shortrange detection is activated
    """
    def __init__(self, x, y, theta = None, speed = None, func_ptr = None, func_param = None, not_avoid = False):
        self.x = x
        self.y = y
        self.theta = theta
        self.action = func_ptr
        self.action_param = func_param
        self.speed = speed
        self.not_avoid = not_avoid

<<<<<<< HEAD
def get_strat(color, actuators):
    """
    Returns a queue of Tasks according to the color of the team, orange or green
    """
    if color == 'green':
        return get_strat_green(actuators)
=======
def get_strat(color, actuators, robot):
    print('color')
    if color == 'green':
        if robot == 'pal':
            return get_strat_green_pal(actuators)
        else:
            return get_strat_green_pmi(actuators)
>>>>>>> PMI: Homologation AI
    else:
        return get_strat_orange(actuators)

def get_strat_orange(actuators):
    """
    Returns the queue of Tasks done by the orange team
    """
    res = queue.Queue()
    res.put(Task(800,  2240, not_avoid=True))
    res.put(Task(1200, 2240))
    res.put(Task(1650, 2700))    
    res.put(Task(1650, 2750, theta=pi, func_ptr=actuators.open_arm, not_avoid=True))
    res.put(Task(1850, 2750, func_ptr=actuators.launch_bee, not_avoid=True))
    res.put(Task(1550, 2780, func_ptr=actuators.close_arm))
    res.put(Task(600,  2550))
    res.put(Task(350,  2550, not_avoid=True))
    res.put(Task(815,  2600))
    res.put(Task(950,  2170))
    res.put(Task(600,  2150))
    res.put(Task(350,  2160, not_avoid=True))
    return res

def get_strat_green(actuators):
    """
    Returns the queue of Tasks done by the green team
    """
    res = queue.Queue()
    res.put(Task(1200, 760))
    res.put(Task(1200, 760))
    res.put(Task(1650, 300))    
    res.put(Task(1650, 250, theta=pi, func_ptr=actuators.open_arm, not_avoid=True))
    res.put(Task(1850, 250, func_ptr=actuators.launch_bee, not_avoid=True))
    res.put(Task(1550, 220, func_ptr=actuators.close_arm))
    res.put(Task(600,  450))
    res.put(Task(350,  450, not_avoid=True))
    res.put(Task(815,  400))
    res.put(Task(950,  830))
    res.put(Task(600,  850))
    res.put(Task(350,  840, not_avoid=True))
    return res

<<<<<<< HEAD
def get_test():
    res = queue.Queue()
    res.put(Task(0, 1500, False, not_avoid=True))
    res.put(Task(0, 0, False, not_avoid=False))
    res.put(Task(0, 1500, False, not_avoid=True))
    return res
=======
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

>>>>>>> PMI: Homologation AI
