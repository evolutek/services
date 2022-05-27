from cellaserv.proxy import CellaservProxy
from math import pi
from time import sleep

ROBOT = 'pal'
x = 340
y = 810
cs: CellaservProxy = CellaservProxy()


def galery_sample_flip():
    cs.robot[ROBOT].set_elevator_config(arm=1, config=3)
    input()
    cs.robot[ROBOT].set_elevator_config(arm=2, config=3)
    input()
    cs.robot[ROBOT].set_elevator_config(arm=3, config=3)
    input()
    cs.robot[ROBOT].set_head_config(arm=1, config=3)
    input()
    cs.robot[ROBOT].set_head_config(arm=2, config=3)
    input()
    cs.robot[ROBOT].set_head_config(arm=3, config=3)
    input()
    cs.robot[ROBOT].goto(x, y)
    input()
    cs.actuators[ROBOT].pumps_get(ids='1')
    input()
    cs.actuators[ROBOT].pumps_get(ids='2')
    input()
    cs.actuators[ROBOT].pumps_get(ids='3')
    input()
    cs.robot[ROBOT].goto(x+50, y)
    input()
    cs.actuators[ROBOT].pumps_drop(ids='1')
    input()
    cs.actuators[ROBOT].pumps_drop(ids='2')
    input()
    cs.actuators[ROBOT].pumps_drop(ids='3')
    input()
    cs.robot[ROBOT].goto(x + 50, y)
    input()
    cs.robot[ROBOT].set_head_config(arm=1, config=1)
    input()
    cs.robot[ROBOT].set_head_config(arm=2, config=1)
    input()
    cs.robot[ROBOT].set_head_config(arm=3, config=1)
    input()
    cs.robot[ROBOT].goto(x - 50, y)
    input()
    cs.actuators[ROBOT].pumps_get(ids='1')
    input()
    cs.actuators[ROBOT].pumps_get(ids='2')
    input()
    cs.actuators[ROBOT].pumps_get(ids='3')
    input()

if __name__ == '__main__':
    galery_sample_flip()
