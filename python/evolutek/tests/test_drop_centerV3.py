from cellaserv.proxy import CellaservProxy
from math import pi
from time import sleep

ROBOT = 'pal'

cs = CellaservProxy()
robot = cs.robot[ROBOT]
trajman = cs.trajman[ROBOT]

robot.set_pos(1400, 1705, 0)
input()

cs.trajman[ROBOT].unfree()
robot.pumps_get(ids=[1, 4, 7, 8, 9, 10])
input()

robot.front_arm_close()
input()

robot.pumps_get(ids=[5])
robot.goto(1750, 1705)
input()

robot.goth(pi/2)
robot.recalibration(x=False, x_sensor='right', decal_y=1511)
input()

robot.pumps_get(ids=[3])
robot.goto(1720, 1855)
input()

robot.goto(1780, 1800)
robot.goth(0)
input()

robot.pumps_get(ids=[2])
robot.goto(1810, 1680)
input()

robot.goto(1780, 1800)
robot.goth(0)
input()

robot.pumps_get(ids=[6])
robot.goto(1810, 1910)
input()

robot.goto(1780, 1800)
robot.goth(0)
input()

robot.goto(1810, 1800)
input()

trajman.move_trsl(dest=50, acc=1000, dec=1000, maxspeed=1000, sens=0)
robot.pumps_drop(ids=[2, 3, 5, 6])
robot.goto(1700, 1800)
input()

robot.front_arm_open()
robot.goto(1720, 1800)
input()

robot.pumps_drop(ids=[1, 3, 4, 5])
sleep(1)
robot.goto(1500, 1800)
input()

robot.goth(pi)
robot.left_cup_holder_drop()
robot.right_cup_holder_drop()
input()

robot.goto(1620, 1800)
input()

robot.pumps_drop(ids=[7, 10])
robot.goto(1580, 1800)
input()

robot.goth(3*pi/4)
input()

robot.pumps_drop(ids=[9])
robot.left_cup_holder_close()
robot.right_cup_holder_close()
input()

robot.goto(1540, 1800)
robot.goth(-3*pi/4)
robot.left_cup_holder_drop()
input()

robot.pumps_drop(ids=[8])
robot.left_cup_holder_close()
input()

robot.goth(pi)
input()
