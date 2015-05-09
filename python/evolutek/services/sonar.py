#!/usr/bin/env python3

import ctypes
import os
import time
import mraa

from cellaserv.service import Service
    
class Sonar (Service):
    def __init__(self, trigger):
        super().__init__(identification=str(trigger))
        self.trigger = trigger
        self.mraa = mraa

    @Service.action
    def get_distance(self):
        self.mraa.Gpio(self.trigger).dir(mraa.DIR_OUT.write(0))
        time.sleep(0.5)
        self.mraa.Gpio(self.trigger).dir(mraa.DIR_OUT.write(1))
        time.sleep(0.00001)
        self.mraa.Gpio(self.trigger).dir(mraa.DIR_OUT.write(0))
        start = time.time()
        while self.mraa.Gpio(self.trigger+1).dir(mraa.DIR_IN.read()) == 0:
            start = time.time()
        while self.mraa.Gpio(self.trigger+1).dir(mraa.DIR_IN.read()) == 1:
            stop = time.time()
        distance = (stop-start)*17000
        self.mraa.Gpio(self.trigger).dir(mraa.DIR_OUT.write(0))
        return (distance)

def main():
    sonarss = [Sonar(trigger=i) for i in [1,3,5,7]] #Define trigger output and eco input and apply get_distance to each sharp   
    Service.loop()

if __name__ == "__main__":
    main()
    
    
        
        
        
     
 
