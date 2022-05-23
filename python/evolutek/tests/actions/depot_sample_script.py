from cellaserv.proxy import CellaservProxy
from math import pi
from time import sleep

ROBOT = 'pal'

def test():
    cs: CellaservProxy = CellaservProxy()
    cs.robot[ROBOT].set_pos(x=400, y=820, theta=pi)

# Dépôt inférieur

    cs.robot[ROBOT].set_elevator_config(arm=1, config=2)
    sleep(0.5)
    cs.robot[ROBOT].set_elevator_config(arm=2, config=2)
    sleep(0.5)
    cs.robot[ROBOT].set_elevator_config(arm=3, config=2)
    input()
    cs.robot[ROBOT].set_head_config(arm=1, config=3)
    sleep(0.5)
    cs.robot[ROBOT].set_head_config(arm=2, config=3)
    sleep(0.5)
    cs.robot[ROBOT].set_head_config(arm=3, config=3)
    input()
    cs.actuators[ROBOT].pumps_get(ids='1') #a enlever
    sleep(0.5)
    cs.actuators[ROBOT].pumps_get(ids='2')#a enlever
    sleep(0.5)
    cs.actuators[ROBOT].pumps_get(ids='3')#a enlever
    input()
    cs.trajman[ROBOT].move_trsl(dest=240, acc=300, dec=300, maxspeed=200, sens=1)
    input()
    cs.robot[ROBOT].set_head_config(arm=1, config=2)
    sleep(0.5)
    cs.robot[ROBOT].set_head_config(arm=2, config=2)
    sleep(0.5)
    cs.robot[ROBOT].set_head_config(arm=3, config=2)
    input()
    cs.actuators[ROBOT].pumps_drop(ids='1')
    sleep(0.5)
    cs.actuators[ROBOT].pumps_drop(ids='2')
    sleep(0.5)
    cs.actuators[ROBOT].pumps_drop(ids='3')
    input()
    # A modifier en goto()
    cs.trajman[ROBOT].move_trsl(dest=240, acc=300, dec=300, maxspeed=200, sens=0)
    input()


if __name__ == '__main__':
    test()
