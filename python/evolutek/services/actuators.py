#!/usr/bin/env python3

from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service
from evolutek.lib.settings import ROBOT
from math import pi
from threading import Thread
from time import sleep


@Service.require("trajman", ROBOT)
class Actuators(Service):
    def __init__(self):
        super().__init__(ROBOT)
        self.cs = CellaservProxy()
        self.trajman = self.cs.trajman[ROBOT]
        self.enabled = True

    @Service.action
    def recalibrate(self, x=True, y=True, side=False, sens_x=False, sens_y=False, dist_x=80, dist_y=80, pos_x=220, pos_y=220, theta=0):
        Thread(target=self.recalibration, args=[x, y, side, sens_x, sens_y, dist_x, dist_y, pos_x, pos_y, theta]).start()
        return 'Done'

    def recalibration(self, x=True, y=True, side=False, sens_x=False, sens_y=False, dist_x=80, dist_y=80, pos_x=220, pos_y=220, theta=0):
        if not self.enabled:
            return

        # Save speeds
        speeds = self.trajman.get_speeds()

        # Check params
        if isinstance(x, str):
            x = x == "true"
        if isinstance(y, str):
            y = y == "true"
        if isinstance(sens_x, str):
            sens_x = sens_x == "true"
        if isinstance(sens_y, str):
            sens_y = sens_y == "true"
        if isinstance(side, str):
            side = side == "true"
        dist_x = int(dist_x)
        dist_y = int(dist_y)
        pos_x = float(pos_x)
        pos_y = float(pos_y)
        theta = float(theta)

        # Set theta, max speed, x and y
        self.trajman.free()
        self.trajman.set_trsl_max_speed(200)
        self.trajman.set_trsl_acc(200)
        self.trajman.set_trsl_dec(200)
            
        self.trajman.set_theta(theta)
        self.trajman.set_x(pos_x)
        self.trajman.set_y(pos_y)

        # Recalibrate X
        if x:
            print('[ACTUATORS] Recalibration X')
            self.trajman.goto_theta(pi if sens_x ^ side else 0)
            while self.trajman.is_moving():
                sleep(0.1)
            self.trajman.recalibration(sens=int(side))
            while self.trajman.is_moving():
                sleep(0.1)
            print('[ACTUATORS] X pos found')
            sleep(0.5)
            position = self.trajman.get_position()
            new_x = position['x'] + dist_x if not sens_x else position['x'] - dist_x
            self.trajman.goto_xy(x=new_x, y=position['y'])
            while self.trajman.is_moving():
                sleep(0.1)

        # Recalibrate Y
        if y:
            print('[ACTUATORS] Recalibration Y')
            self.trajman.goto_theta(- pi / 2 if sens_y ^ side else pi /2)
            while self.trajman.is_moving():
                sleep(0.1)
            self.trajman.recalibration(int(side))
            while self.trajman.is_moving():
                sleep(0.1)
            print('[ACTUTATORS] Y pos found')
            sleep(0.5)
            position = self.trajman.get_position()
            new_y = position['y'] + dist_y if not sens_y else position['y'] - dist_y
            print(new_y)
            self.trajman.goto_xy(x=position['x'], y=new_y)
            while self.trajman.is_moving():
                sleep(0.1)

        # Set back trajman params
        self.trajman.set_trsl_max_speed(speeds['trmax'])
        self.trajman.set_trsl_acc(speeds['tracc'])
        self.trajman.set_trsl_dec(speeds['trdec'])

        print('[ACTUATORS] Recalibration done')
        self.publish('recalibrated')

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
