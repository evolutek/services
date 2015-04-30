#!/usr/bin/env python3

import ctypes
import os
import time
import cellaserv.proxy

from cellaserv.service import Service

    
class  ElevatorRight(Service):
    def __init__(self, ax):
        super().__init__(identification=str(trigger))
        self.ax = ax

    @Service.action
    def stack(self):
	robot.ax["2"].move(goal = 540)
	time.sleep(minimal_delay)
	robot.ax["3"].move(goal = 480)
	time.sleep(minimal_delay)
	robot.ax["4"].move(goal = 0)
	time.sleep(minimal_delay)
	robot.ax["5"].move(goal = 1000)
	time.sleep(minimal_delay)
	robot.ax["1"].move(goal = 1000)
	time.sleep(minimal_delay)
	robot.ax["4"].move(goal = 540)
	time.sleep(minimal_delay)
	robot.ax["5"].move(goal = 480)
	time.sleep(minimal_delay)
	robot.ax["2"].move(goal = 0)
	time.sleep(minimal_delay)
	robot.ax["3"].move(goal = 1020)
	time.sleep(minimal_delay)
	count = count + 1
	
    @Service.action
    def pop(self):
        if count = 0:
            return ("error : cant pop an empty stack")
	
    @Service.action
    def init(self)
	robot.ax["1"].move(goal = 260)
	time.sleep(minimal_delay)
	robot.ax["2"].move(goal = 0)
	time.sleep(minimal_delay)
	robot.ax["3"].move(goal = 1020)
	time.sleep(minimal_delay)
	
    @Service.action
    def count(self):
        return count

def main():
    count= 0;
	minimal_delay = 0.8;
    robot = cellaserv.proxy.CellaservProxy()
    axs = [Ax(ax=i) for i in [1,2,3,4,5]] #Define axs and apply each operation to them (ax : monte,droite,gauche,hgauche,hdroite)
	for n in [1,2,3,4,5] :
		robot.ax[n].mode_joint()
    
	 robot.ax["5"].move(goal=1000)
	 time.sleep(minimal_delay)
	 robot.ax["4"].move(goal=0)
	 time.sleep(minimal_delay)

if __name__ == "__main__":
    main()
    
    
        
        
        
     
 
