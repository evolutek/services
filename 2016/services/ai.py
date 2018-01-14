#!/usr/bin/env python3

from evolutek.services.watchdog import Watchdog
from queue import *
from math import pi
from time import sleep
from threading import Thread, Timer, Event
from cellaserv.service import Service, ConfigVariable
from cellaserv.proxy import CellaservProxy
from evolutek.services.objective import *

@Service.require("trajman", "pal")
class ia(Service):

    def __init__(self):
        super().__init__()
        self.cs = CellaservProxy()
        self.color = self.cs.config.get(section='match', option='color')
        self.pattern = int(self.cs.config.get(section = 'match', option='pattern'))
        self.sharp_period = ConfigVariable(section='sharp', option='period')
        self.objectives = Objective(self.color, self.pattern)
        self.queue = LifoQueue()
        for i in range(len(self.objectives.moves)-1, -1, -1):
            if i == 0:
                self.queue.put("max")
            self.queue.put(self.objectives.moves[i])
        self.trajman = self.cs.trajman['pal']
        self.actuators = self.cs.actuators['pal']
        self.stop_time = Timer(89, self.match_stop)
        self.current_move = None
        self.thread = Thread(target=self.start)
        self.thread.daemon = True
        self.stop_move = Event()
        self.watchdog = Watchdog(0.5, self.restart_move)
        self.control = False
        self.maxspeed = 600
        self.minspeed = 300
        self.setup()

    @Service.event
    def match_start(self):
        print("Go")
        self.stop_time.start()
        self.thread.start()
    
    @Service.event
    def sharp_avoid(self):
        print("avoid")
        self.stop_move.set()
        self.queue.put(self.current_move)
        self.watchdog.reset()

    def control_sharp(self, out):
        self.cs.sharp['pal'].control(par=out)

    def restart_move(self):
        print("restart move")
        self.stop_move = Event()
        print(self.stop_move.is_set())

    def match_stop(self):
        print("Stop")
        self.trajman['pal'].free()
        self.actuators.open_umbrella()
        self.trajman['pal'].disable()
        self.cs.ax['1'].free()
        self.cs.ax['2'].free()
        self.cs.ax['4'].free()
        self.cs.ax['5'].free()

    def setup(self):
        print(self.color)
        if self.color == "green":
            print("It's green")
            self.trajman.set_theta(0)
            self.trajman.set_x(2850)
        else:
            print("It's purple")
            self.trajman.set_theta(pi)
            self.trajman.set_x(150)
        self.trajman.set_y(1000)
        print("Pattern is : " + str(self.pattern))
        self.trajman.set_y(1000)
        self.actuators.close_umbrella()
        self.actuators.close_arm()
        print("Setup complete")

    def start(self):
        print("Starting the match")
        self.control_sharp(self.control)
        self.trajman.set_trsl_max_speed(self.minspeed)
        while not self.queue.empty():
            if not self.stop_move.is_set():
                move = self.queue.get()
                if move == "max":
                    self.trajman.set_trsl_max_speed(self.maxspeed)
                else :
                    if move != None:
                        print("Starting : " + str(move))
                        self.current_move = move
                        if move.theta != None:
                            self.goto_theta(move.theta)
                        print("1")
                        if move.action != None:
                            action = move.action
                            if action == 1:
                                self.actuators.open_door()
                            elif action == 2:
                                self.actuators.close_door()
                            elif action == 3:
                                self.actuators.half_close_door()
                            elif action == 5:
                                self.actuators.open_arm_right()
                            elif action == 6:
                                self.actuators.open_arm_left()
                            elif action == 7:
                                self.actuators.half_open_arm()
                            elif action == 8:
                                self.actuators.close_arm()
                            elif action == 9:
                                self.actuators.activate_ea()
                                self.trajman.set_trsl_max_speed(self.minspeed)
                            else:
                                self.actuators.disable_ea()
                            sleep(2)
                        print("2")
                        if move.control != self.control:
                            self.control = move.control
                            self.control_sharp(self.control)
                        print("3")
                        if move.x != None and move.y != None:
                            print("4")
                            self.goto_xy(x=move.x, y=move.y)

    def goto_xy(self, x, y):
        self.trajman.goto_xy(x=x, y=y)
        while self.trajman.is_moving():
            continue
        sleep(1)
        

    def goto_theta(self, theta):
        self.trajman.goto_theta(theta=theta)
        while self.trajman.is_moving():
            continue
def main():
    ai = ia()
    ai.run()

if __name__  == '__main__':
    main()
