#!/usr/bin/env python3

import ctypes
import os
from time import sleep
import cellaserv.proxy

from cellaserv.service import Service

    
class  ElevatorForward(Service):
    count= 0
    minimal_delay = 0.8
    robot = cellaserv.proxy.CellaservProxy()
    def __init__(self):
       for n in [1,2,3,4,5] :
	   self.robot.ax[n].mode_joint()
       self.robot.ax["5"].move(goal=1000)
       time.sleep(minimal_delay)
       self.robot.ax["4"].move(goal=0)
       time.sleep(minimal_delay)
       self.robot.ax["1"].move(goal = 260)
       time.sleep(minimal_delay)
       self.robot.ax["2"].move(goal = 0)
       time.sleep(minimal_delay)
       self.robot.ax["3"].move(goal = 1020)
       time.sleep(minimal_delay)
       print("ForwardElevator : Init Done")
       

    @Service.action
    def stack(self):
	self.robot.ax["2"].move(goal = 540)
	time.sleep(minimal_delay)
	self.robot.ax["3"].move(goal = 480)
	time.sleep(minimal_delay)
	self.robot.ax["4"].move(goal = 0)
	time.sleep(minimal_delay)
	self.robot.ax["5"].move(goal = 1000)
	time.sleep(minimal_delay)
	self.robot.ax["1"].move(goal = 1000)
	time.sleep(minimal_delay)
	self.robot.ax["4"].move(goal = 540)
	time.sleep(minimal_delay)
	self.robot.ax["5"].move(goal = 480)
	time.sleep(minimal_delay)
	self.robot.ax["2"].move(goal = 0)
	time.sleep(minimal_delay)
	self.robot.ax["3"].move(goal = 1020)
	time.sleep(minimal_delay)
	count = count + 1
	print("ForwardElevtor : Stack Done")
	
    @Service.action
    def pop(self):
        if count = 0:
            return ("error : cant pop an empty stack")
	
	
    @Service.action
    def count(self):
        print(count)
        return count

def main():
    Poney = ElevatorForward()
    Service.loop()

if __name__ == "__main__":
    main()
    
    
        
        
        
     
 
