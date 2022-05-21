from cellaserv.proxy import CellaservProxy
from math import pi
from time import sleep

def test():
    cs: CellaservProxy = CellaservProxy()
    cs.trajman['pmi'].free()
    cs.robot['pmi'].set_pos(x=1800, y=1130, theta=pi)
    cs.trajman['pmi'].unfree()

    cs.robot["pmi"].set_elevator_config(arm=1, config=0)
    input()
    cs.robot["pmi"].set_elevator_config(arm=3, config=0)
    input()
    cs.robot["pmi"].set_elevator_config(arm=2, config=0)
    input()
    cs.robot["pmi"].goto(90, 1130)
    input()
    cs.robot['pmi'].set_elevator_config(arm=1, config=4)
    input()
    cs.robot['pmi'].set_elevator_config(arm=3, config=4)
    input()
    cs.robot['pmi'].set_elevator_config(arm=3, config=4)

    #
    # cs.actuators['pmi'].pumps_get(ids='2')
    # cs.robot['pmi'].set_elevator_config(arm=2, config=5)
    # sleep(0.5)
    # cs.actuators['pmi'].pumps_drop(ids='4')
    # input()
    # cs.robot["pmi"].set_head_config(arm=2, config=2)
    # input()
    # cs.robot['pmi'].set_elevator_config(arm=2, config=2)
    # input()
    # cs.robot["pmi"].goto(120, 225)
    # input()
    # cs.actuators['pmi'].pumps_drop(ids='2')
    # input()
    # cs.robot["pmi"].goto(250, 225)
    # input()
    # cs.robot['pmi'].set_head_config(arm=2, config=0)
    # input()
    # cs.robot['pmi'].set_elevator_config(arm=2, config=5)
    # input()

if __name__ == '__main__':
    test()
