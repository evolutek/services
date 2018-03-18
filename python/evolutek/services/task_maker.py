# -*- coding: utf-8 -*-
"""
Created on Fri Mar 16 15:06:29 2018

@author: marko
"""

import queue

import tasks

class Task:
    def __init__(self, x, y, theta = None, speed = None, func_ptr = None, not_avoid = False):
        self.x = x
        self.y = y
        self.theta = theta
        self.action = func_ptr
        self.speed = speed
        self.not_avoid = not_avoid
        


def get_strat_orange():
    res = queue.Queue()
    res.put(Task(2700, 1000))
    res.put(Task(2400, 300))
    
    return res


def get_strategy(filename, is_green = True):
    """
    Read a file that contains the list of tasks (coordinates x, y, theta,
    func_id and boolean)
    and returns a queue of tasks
    
    strat_file = open(filename, 'r')
    res = queue.Queue()
    line = strat_file.readline()
    
    while line:
        instrs = line.split(';')
	#todo : take into account the team color when adding objectives
        res.put(Task(int(instrs[0]), int(instrs[1]), int(instrs[2]), \
                 tasks.get_task(instrs[3]), instrs[4] == 't'))
        line = strat_file.readline()    
    
    return res"""
    pass
