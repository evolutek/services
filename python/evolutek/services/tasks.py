# -*- coding: utf-8 -*-
"""
Created on Fri Mar 16 15:16:02 2018

@author: marko
"""

from math import pi

def dance_not(trajman):
    trajman.mov_rot(pi/4, 5, 5, 1000, 0)
    trajman.mov_rot(pi/4, 5, 5, 1000, 1)

actions = {"dance" : dance_not}

def get_task(func_name) :
    """
    takes a string functionname (function id) and returns a pointer to the
    corresponding function from actions
    """
    if func_name.lower() == 'none':
         return None
    return actions[func_name]
