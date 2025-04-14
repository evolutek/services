from cellaserv.proxy import CellaservProxy
from math import pi
from time import sleep

def test():
    cs: CellaservProxy = CellaservProxy()
    cs.trajman['pmi'].free()
    cs.robot['pmi'].set_pos(x=250, y=225, theta=pi)
    cs.trajman['pmi'].unfree()
    cs.actuators['pmi'].pumps_get(ids='4')
    cs.robot["pmi"].set_head_config(arm=2, config=0)
    input()
    cs.robot['pmi'].set_elevator_config(arm=2, config=2)
    print('Please poot the statuette')
    input()
    cs.actuators['pmi'].pumps_get(ids='2')
    cs.robot['pmi'].set_elevator_config(arm=2, config=5)
    sleep(0.5)
    cs.actuators['pmi'].pumps_drop(ids='4')
    input()
    cs.robot["pmi"].set_head_config(arm=2, config=2)
    input()
    cs.robot['pmi'].set_elevator_config(arm=2, config=2)
    input()
    cs.robot["pmi"].goto(120, 225)
    input()
    cs.actuators['pmi'].pumps_drop(ids='2')
    input()
    cs.robot["pmi"].goto(250, 225)
    input()
    cs.robot['pmi'].set_head_config(arm=2, config=0)
    input()
    cs.robot['pmi'].set_elevator_config(arm=2, config=5)
    input()

if __name__ == '__main__':
    test()
