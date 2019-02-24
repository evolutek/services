#!/usr/bin/env python3

from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service, ConfigVariable
from evolutek.lib.settings import ROBOT
from math import pi
from threading import Thread
from time import sleep

@Service.require("ax", "1")
@Service.require("ax", "2")
@Service.require("ax", "3")
@Service.require("ax", "4")
@Service.require("trajman", ROBOT)
class Actuators(Service):

    robot_size_x = ConfigVariable(section=ROBOT, option="robot_size_x", coerc=float)
    robot_size_y = ConfigVariable(section=ROBOT, option="robot_size_y", coerc=float)

    def __init__(self):
        super().__init__(ROBOT)
        self.cs = CellaservProxy()
        self.trajman = self.cs.trajman[ROBOT]
        self.enabled = True
        self.dist = ((self.robot_size_x() ** 2 + self.robot_size_y() ** 2) ** (1 / 2.0)) + 50

        for n in [1, 2, 3, 4]:
            self.cs.ax[str(n)].mode_joint()
        self.reset()

    @Service.action
    def reset(self):
        self.enabled = True
        self.close_arms()
        self.close_clapet()

    @Service.action
    def close_arms(self):
        self.cs.ax['1'].move(goal=136)
        self.cs.ax['2'].move(goal=150)
        self.cs.ax['3'].move(goal=136)

    @Service.action
    def open_arms(self):
        self.cs.ax['1'].move(goal=498)
        self.cs.ax['2'].move(goal=512)
        self.cs.ax['3'].move(goal=498)

    @Service.action
    def open_arm_goldenium(self):
        self.cs.ax['2'].move(goal=220)

    @Service.action
    def close_clapet(self):
        self.cs.ax['4'].move(goal=490)

    @Service.action
    def open_clapet(self):
        self.cs.ax['4'].move(goal=710)

    @Service.action
    def free(self):
        for n in [1, 2, 3, 4]:
            self.cs.ax[str(n)].free()

    @Service.action
    def recalibrate(self, x=True, y=True, side=False, sens_x=False, sens_y=False, decal_x=0, decal_y=0, init=False):
        Thread(target=self.recalibration, args=[x, y, side, sens_x, sens_y, decal_x, decal_y, init]).start()
        return 'Done'

    def recalibration(self, x=True, y=True, side=False, sens_x=False, sens_y=False, decal_x=0, decal_y=0, init=False):
        if not self.enabled:
            return

        # Save speeds
        speeds = self.trajman.get_speeds()

        # Check params
        if isinstance(x, str):
            x = x == "true"
        if isinstance(y, str):
            y = y == "true"
        if isinstance(side, str):
            side = side == "true"
        if isinstance(sens_x, str):
            sens_x = sens_x == "true"
        if isinstance(sens_y, str):
            sens_y = sens_y == "true"
        decal_x = float(decal_x)
        decal_y = float(decal_y)
        if isinstance(init, str):
            init = init == "true"

        # Set theta, max speed, x and y
        self.trajman.free()
        self.trajman.set_trsl_max_speed(200)
        self.trajman.set_trsl_acc(200)
        self.trajman.set_trsl_dec(200)

        if init:
            self.trajman.set_theta(0)
            self.trajman.set_x(1000)
            self.trajman.set_y(1000)

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
            pos_x = position['x'] + decal_x if not sens_x else position['x'] - decal_x
            self.trajman.set_x(pos_x)
            new_x = pos_x + self.dist - self.robot_size_x() if not sens_x else pos_x - self.dist + self.robot_size_x()
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
            pos_y = position['y'] + decal_y if not sens_y else position['y'] - decal_y
            self.trajman.set_y(pos_y)
            new_y = pos_y + self.dist - self.robot_size_y() if not sens_y else pos_y - self.dist + self.robot_size_y()
            print(new_y)
            self.trajman.goto_xy(x=position['x'], y=new_y)
            while self.trajman.is_moving():
                sleep(0.1)

        # Set back trajman params
        self.trajman.set_trsl_max_speed(speeds['trmax'])
        self.trajman.set_trsl_acc(speeds['tracc'])
        self.trajman.set_trsl_dec(speeds['trdec'])

        print('[ACTUATORS] Recalibration done')
        self.publish(ROBOT + '_recalibrated')

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
