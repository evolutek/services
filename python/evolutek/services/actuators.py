#!/usr/bin/env python3

from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service, ConfigVariable
from evolutek.lib.settings import ROBOT
from evolutek.lib.watchdog import Watchdog
from threading import Event
from math import pi
from time import sleep
import os


##TODO: DISABLE not working

@Service.require("ax", "1")
@Service.require("ax", "2")
@Service.require("ax", "3")
@Service.require("ax", "4")
@Service.require("gpios", ROBOT)
@Service.require("trajman", ROBOT)
class Actuators(Service):

    robot_size_x = ConfigVariable(section=ROBOT, option="robot_size_x", coerc=float)
    robot_size_y = ConfigVariable(section=ROBOT, option="robot_size_y", coerc=float)

    def __init__(self):
        super().__init__(ROBOT)
        self.cs = CellaservProxy()
        self.enabled = True
        self.dist = ((self.robot_size_x() ** 2 + self.robot_size_y() ** 2) ** (1 / 2.0)) + 50
        self.color = 'yellow'
        self.color1 = self.cs.config.get(section='match', option='color1')
        #self.timeout_ejecteur = float(self.cs.config.get(section='ROBOT', option='timeout_ejecteur'))
        self.timeout_ejecteur = 5

        try:
            self.color = self.cs.match.get_match()['color']
        except Exception as e:
            print("Failed to get color: %s" % str(e))

        for n in [1, 2, 3, 4]:
            self.cs.ax[str(n)].mode_joint()

        self.cs.ax['4'].moving_speed(256)

        self.ejecteur_event = Event()
        self.reset()

    def handler_timeout_ejecteur(self):
        self.ejecteur_event.set()

    @Service.action
    def reset(self, color=None):
        if color is not None:
            self.color = color

        self.enabled = True
        self.disable_suction_arms()
        self.disable_suction_goldenium()
        self.close_arms()
        self.reset_ejecteur()
        self.close_clapet()
        self.init_ejecteur()

    """ FREE """
    @Service.action
    def free(self):
        self.disable_suction_arms()
        self.disable_suction_goldenium()
        for n in [1, 2, 3, 4]:
            self.cs.ax[str(n)].free()

    @Service.action
    def wait(self, time):
        sleep(float(time))

    """ ARMS """
    @Service.action
    def close_arms(self):
        self.cs.ax['1'].moving_speed(128)
        self.cs.ax['2'].moving_speed(128)
        self.cs.ax['3'].moving_speed(128)
        self.cs.ax['1'].move(goal=121)
        self.cs.ax['2'].move(goal=121)
        self.cs.ax['3'].move(goal=121)
        sleep(1.5)
        self.cs.ax['1'].moving_speed(512)
        self.cs.ax['2'].moving_speed(512)
        self.cs.ax['3'].moving_speed(512)


    """ ARMS """
    @Service.action
    def close_arms_off(self):
        self.cs.ax['1'].moving_speed(256)
        self.cs.ax['2'].moving_speed(256)
        self.cs.ax['3'].moving_speed(256)
        self.cs.ax['1'].move(goal=214)
        self.cs.ax['2'].move(goal=214)
        self.cs.ax['3'].move(goal=214)
        sleep(1)
        self.cs.ax['1'].moving_speed(512)
        self.cs.ax['2'].moving_speed(512)
        self.cs.ax['3'].moving_speed(512)

    @Service.action
    def open_arms(self):
        self.cs.ax['1'].move(goal=492)
        self.cs.ax['2'].move(goal=492)
        self.cs.ax['3'].move(goal=492)
        sleep(0.5)

    @Service.action
    def lower_palet(self):
        self.cs.ax['1'].move(goal=225)
        self.cs.ax['2'].move(goal=225)
        self.cs.ax['3'].move(goal=225)
        sleep(0.15)
        self.cs.ax['1'].move(goal=121)
        self.cs.ax['2'].move(goal=121)
        self.cs.ax['3'].move(goal=121)
        sleep(0.15)

    @Service.action
    def enable_suction_arms(self):
        self.cs.gpios[ROBOT].write_gpio(value=False, name="relayArms")

    @Service.action
    def disable_suction_arms(self):
        self.cs.gpios[ROBOT].write_gpio(value=True, name="relayArms")

    @Service.action
    def get_palet(self):
        self.open_arms()
        self.enable_suction_arms()

        self.cs.trajman[ROBOT].move_trsl(dest=100, acc=100, dec=100, maxspeed=400, sens=1)
        while self.cs.trajman[ROBOT].is_moving():
            sleep(0.1)

        self.cs.trajman[ROBOT].move_trsl(dest=100, acc=100, dec=100, maxspeed=400, sens=0)
        while self.cs.trajman[ROBOT].is_moving():
            sleep(0.1)
        
        self.close_arms_off()

    """ GOLDENIUM """
    @Service.action
    def open_arm_goldenium(self):
        self.cs.ax['2'].move(goal=205)
        sleep(0.25)

    @Service.action
    def enable_suction_goldenium(self):
        self.cs.gpios[ROBOT].write_gpio(value=False, name="relayGold")

    @Service.action
    def disable_suction_goldenium(self):
        self.cs.gpios[ROBOT].write_gpio(value=True, name="relayGold")

    @Service.action
    def get_goldenium(self):
        self.open_arm_goldenium()
        self.enable_suction_goldenium()

        self.cs.trajman[ROBOT].move_trsl(dest=50, acc=100, dec=100, maxspeed=400, sens=1)
        while self.cs.trajman[ROBOT].is_moving():
            sleep(0.1)

        self.cs.ax['2'].moving_speed(256)
        self.cs.ax['2'].move(goal=214)
        self.cs.ax['2'].moving_speed(512)
        sleep(0.5)

        self.cs.trajman[ROBOT].move_trsl(dest=50, acc=100, dec=100, maxspeed=400, sens=0)
        while self.cs.trajman[ROBOT].is_moving():
            sleep(0.1)

    @Service.action
    def drop_goldenium(self):
        self.open_arm_goldenium()

        self.cs.trajman[ROBOT].move_trsl(dest=50, acc=100, dec=100, maxspeed=400, sens=1)
        while self.cs.trajman[ROBOT].is_moving():
            sleep(0.1)

        self.disable_suction_goldenium()
        sleep(0.2)

        self.cs.ax['2'].move(goal=400)
        sleep(0.2)

        self.disable_suction_arms()
        sleep(0.2)

        self.cs.ax['2'].move(goal=214)
        sleep(0.5)
        
        self.enable_suction_arms()

    @Service.action
    def get_blue_palet(self):
        #self.open_arms()
        self.cs.ax['2'].move(goal=492)
        sleep(0.5)
        self.enable_suction_arms()

        self.cs.trajman[ROBOT].move_trsl(dest=50, acc=100, dec=100, maxspeed=400, sens=1)
        while self.cs.trajman[ROBOT].is_moving():
            sleep(0.1)

        self.cs.trajman[ROBOT].move_trsl(dest=50, acc=100, dec=100, maxspeed=400, sens=0)
        while self.cs.trajman[ROBOT].is_moving():
            sleep(0.1)

        #self.cs.ax['1'].moving_speed(128)
        #self.cs.ax['3'].moving_speed(128)
        #self.cs.ax['1'].move(goal=121)
        #self.cs.ax['3'].move(goal=121)
        self.cs.ax['2'].move(goal=250)
        sleep(1.5)
        #self.cs.ax['1'].moving_speed(512)
        #self.cs.ax['3'].moving_speed(512)

    @Service.action
    def drop_blue_palet(self):
        self.cs.ax['2'].move(goal=492)
        self.disable_suction_arms()
        sleep(0.2)
        self.cs.ax['2'].move(goal=128)
        sleep(0.5)

    @Service.action
    def drop_palet_rampe(self):
        if self.color == self.color1:
            self.cs.ax['1'].move(goal=494)
        else:
            self.cs.ax['3'].move(goal=494)
        
        sleep(0.5)

        self.cs.trajman[ROBOT].move_trsl(dest=30, acc=100, dec=100, maxspeed=400, sens=0)
        while self.cs.trajman[ROBOT].is_moving():
            sleep(0.1)
        
        if self.color == self.color1:
            self.cs.ax['1'].move(goal=494)
        else:
            self.cs.ax['3'].move(goal=494)
        
        sleep(0.1)

        self.disable_suction_arms()
        
        sleep(0.2)

        self.cs.trajman[ROBOT].move_trsl(dest=20, acc=100, dec=100, maxspeed=400, sens=1)
        while self.cs.trajman[ROBOT].is_moving():
            sleep(0.1)

        sleep(0.2)

        self.cs.trajman[ROBOT].move_trsl(dest=40, acc=100, dec=100, maxspeed=400, sens=0)
        while self.cs.trajman[ROBOT].is_moving():
            sleep(0.1)
        
        if self.color == self.color1:
            self.cs.ax['1'].move(goal=214)
        else:
            self.cs.ax['3'].move(goal=214)
       
        sleep(0.5)

        self.enable_suction_arms()

    """ CLAPET """
    @Service.action
    def close_clapet(self):
        self.cs.ax['4'].move(goal=520)
        sleep(0.5)

    @Service.action
    def half_open_clapet(self):
        self.cs.ax['4'].move(goal=650)
        sleep(0.25)

    @Service.action
    def open_clapet(self):
        self.cs.ax['4'].move(goal=780)
        sleep(0.25)

    # TODO: Update
    @Service.action
    def drop_palet(self):
        self.open_arms()
        self.disable_suction_arms()

    """ Ejecteur """
    ##TODO: Use PWM fct instead of write_gpio
    @Service.action
    def init_ejecteur(self):
        contact = None

        if int(self.cs.gpios[ROBOT].read_gpio(id=4)) == 1:
            self.cs.gpios[ROBOT].write_gpio(value=True, id=19)
            self.cs.gpios[ROBOT].write_gpio(value=False, id=26)
            contact = 22
        else:
            self.cs.gpios[ROBOT].write_gpio(value=False, id=19)
            self.cs.gpios[ROBOT].write_gpio(value=True, id=26)
            contact = 4
        if int(self.cs.gpios[ROBOT].read_gpio(id=contact)) != 1:
            watchdog = Watchdog(1, self.handler_timeout_ejecteur)
            watchdog.reset()
            self.cs.gpios[ROBOT].write_gpio(value=100, id=13)
            while not self.ejecteur_event.isSet() and int(self.cs.gpios[ROBOT].read_gpio(id=contact)) != 1:
                sleep(0.1)
            self.cs.gpios[ROBOT].write_gpio(value=0, id=13)
            watchdog.stop()
            self.ejecteur_event.clear()


    @Service.action
    def reset_ejecteur(self):
        contact = None

        if self.color == self.color1:
            self.cs.gpios[ROBOT].write_gpio(value=False, id=19)
            self.cs.gpios[ROBOT].write_gpio(value=True, id=26)
            contact = 4
        else:
            self.cs.gpios[ROBOT].write_gpio(value=True, id=19)
            self.cs.gpios[ROBOT].write_gpio(value=False, id=26)
            contact = 22
        if int(self.cs.gpios[ROBOT].read_gpio(id=contact)) != 1:
            watchdog = Watchdog(self.timeout_ejecteur, self.handler_timeout_ejecteur)
            watchdog.reset()
            self.cs.gpios[ROBOT].write_gpio(value=100, id=13)
            while not self.ejecteur_event.isSet() and int(self.cs.gpios[ROBOT].read_gpio(id=contact)) != 1:
                sleep(0.1)
            self.cs.gpios[ROBOT].write_gpio(value=0, id=13)
            watchdog.stop()
            self.ejecteur_event.clear()

    @Service.action
    def push_ejecteur(self):
        contact = None

        if self.color != self.color1:
            self.cs.gpios[ROBOT].write_gpio(value=False, id=19)
            self.cs.gpios[ROBOT].write_gpio(value=True, id=26)
            contact = 4
        else:
            self.cs.gpios[ROBOT].write_gpio(value=True, id=19)
            self.cs.gpios[ROBOT].write_gpio(value=False, id=26)
            contact = 22

        if int(self.cs.gpios[ROBOT].read_gpio(id=contact)) != 1:
            watchdog = Watchdog(self.timeout_ejecteur, self.handler_timeout_ejecteur)
            watchdog.reset()
            self.cs.gpios[ROBOT].write_gpio(value=100, id=13)
            while not self.ejecteur_event.isSet() and int(self.cs.gpios[ROBOT].read_gpio(id=contact)) != 1:
                sleep(0.1)
            self.cs.gpios[ROBOT].write_gpio(value=0, id=13)
            watchdog.stop()
            self.ejecteur_event.clear()

    # TODO: test and if it's not working, make a custom with move_trsl
    """ Recalibration """
    @Service.action
    def recalibrate(self, x=True, y=True, side=False, sens_x=False, sens_y=False, decal_x=0, decal_y=0, init=False):
        if not self.enabled:
            return

        # Save speeds
        speeds = self.cs.trajman[ROBOT].get_speeds()

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
        self.cs.trajman[ROBOT].free()
        self.cs.trajman[ROBOT].set_trsl_max_speed(200)
        self.cs.trajman[ROBOT].set_trsl_acc(200)
        self.cs.trajman[ROBOT].set_trsl_dec(200)

        if init:
            self.cs.trajman[ROBOT].set_theta(0)
            self.cs.trajman[ROBOT].set_x(1000)
            self.cs.trajman[ROBOT].set_y(1000)

        # Recalibrate X
        if x:
            print('[ACTUATORS] Recalibration X')
            self.cs.trajman[ROBOT].goto_theta(pi if sens_x ^ side else 0)
            while self.cs.trajman[ROBOT].is_moving():
                sleep(0.1)
            self.cs.trajman[ROBOT].recalibration(sens=int(side))
            while self.cs.trajman[ROBOT].is_moving():
                sleep(0.1)
            print('[ACTUATORS] X pos found')
            sleep(0.5)
            position = self.cs.trajman[ROBOT].get_position()
            pos_x = position['x'] + decal_x if not sens_x else position['x'] - decal_x
            self.cs.trajman[ROBOT].set_x(pos_x)
            new_x = pos_x + self.dist - self.robot_size_x() if not sens_x else pos_x - self.dist + self.robot_size_x()
            self.cs.trajman[ROBOT].goto_xy(x=new_x, y=position['y'])
            while self.cs.trajman[ROBOT].is_moving():
                sleep(0.1)

        # Recalibrate Y
        if y:
            print('[ACTUATORS] Recalibration Y')
            self.cs.trajman[ROBOT].goto_theta(- pi / 2 if sens_y ^ side else pi /2)
            while self.cs.trajman[ROBOT].is_moving():
                sleep(0.1)
            self.cs.trajman[ROBOT].recalibration(int(side))
            while self.cs.trajman[ROBOT].is_moving():
                sleep(0.1)
            print('[ACTUTATORS] Y pos found')
            sleep(0.5)
            position = self.cs.trajman[ROBOT].get_position()
            pos_y = position['y'] + decal_y if not sens_y else position['y'] - decal_y
            self.cs.trajman[ROBOT].set_y(pos_y)
            new_y = pos_y + self.dist - self.robot_size_y() if not sens_y else pos_y - self.dist + self.robot_size_y()
            print(new_y)
            self.cs.trajman[ROBOT].goto_xy(x=position['x'], y=new_y)
            while self.cs.trajman[ROBOT].is_moving():
                sleep(0.1)

        # Set back trajman params
        self.cs.trajman[ROBOT].set_trsl_max_speed(speeds['trmax'])
        self.cs.trajman[ROBOT].set_trsl_acc(speeds['tracc'])
        self.cs.trajman[ROBOT].set_trsl_dec(speeds['trdec'])

        print('[ACTUATORS] Recalibration done')

    @Service.action
    def enable(self):
        self.enabled = True
        print("[ACTUATORS] Enabled")

    @Service.action
    def disable(self):
        self.enabled= False
        print("[ACTUATORS] Disabled")

def wait_for_beacon():
    hostname = "pi"
    while True:
        r = os.system("ping -c 1 " + hostname)
        if r == 0:
            return
        pass

def main():
    wait_for_beacon()
    actuators = Actuators()
    actuators.run()

if __name__ == '__main__':
    main()
