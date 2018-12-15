#!/usr/bin/env python3

from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service
from evolutek.lib.settings import ROBOT
from time import sleep

@Service.require("trajman", ROBOT)
class Actuators(Service):
    def __init__(self):
        super().__init__(ROBOT)
        self.cs = CellaservProxy()
        self.trajman = self.cs.trajman[ROBOT]

        self.enabled = True

    @Service.event 
    def recalibrate(self, x=True, y=True, sens=True, decal_x=0, decal_y=0, init=True):
        if self.enabled:
            #Save values to reset later
            speeds = self.trajman.get_speeds()
            # Get side
            self.side = 1 if color1 == int(self.cs.gpios[ROBOT].read_gpio("color")) else -1
            self.color1 = self.cs.config.get(section='match', option='color1')
            # Set theta, max speed, x and y
            self.trajman.free()
            self.trajman.set_trsl_max_speed(200)
            self.trajman.set_trsl_acc(200)
            self.trajman.set_trsl_dec(200)
            if init:
                self.trajman.set_theta(0)
                self.traman.set_x(1000)
                self.trajman.set_y(1000)
            # Recalibrate

            if x:
                print('[ACTUATORS] Recalibration X')
                sefl.trajman.goto_theta(0)
                self.trajman.recalibration(sens=0 if sens else 1)
                while self.trajman.is_moving():
                    sleep(0.5)
                print('[ACTUATORS] X pos found')
            
                position = self.trajman.get_position()
                self.trajman.set_x(position['x'] + decal_y if sens else -decal_y)
                new_x = 500 + decal_x if sens else 2000 - decal_x
                self.trajman.goto_xy(new_x, position['y'])

            if y:
                print('[ACTUATORS] Recalibration Y')
                if x:
                    self.trajman.goto_theta(math.pi / 2 * -side if sens else side)
                self.trajman.recalibration(sens=0 if sens else 1)
                while self.trajman.is_moving():
                    sleep(0.5)
                print('[ACTUTATORS] Y pos found')
                position = self.trajman.get_position()
                self.trajman.set_x(position['y'] + decal_y if sens else -decal_y)
                new_y = 500 + decal_y if sens else 3000 - decal_y
                self.trajman.goto_xy(position['x'], new_y)
        
            robot.tm.set_trsl_max_speed(speeds['trmax'])
            robot.tm.set_trsl_acc(speeds['tracc'])
            robot.tm.set_trsl_dec(speeds['trdec'])

            print('[ACTUATORS] Recalibration done')

        @Service.action
        def enable(self):
            self.enabled = True
            print("[ACTUATORS] Enabled")

        @Service.action
        def disable(self):
            self.enabled= False
            print("[ACTUATORS] Disabled")

def main():
    actuators = Actuators()
    actuators.run()

if __name__ == '__main__':
    main()
        
