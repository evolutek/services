from cellaserv.proxy import CellaservProxy
from math import pi

def test():
    cs: CellaservProxy = CellaservProxy()
    cs.robot['pmi'].set_pos(x=250, y=225, theta=pi)
    cs.actuators['pmi'].pumps_get(ids='4')
    input()
    cs.actuators['pmi'].pumps_drop(ids='4')
    cs.actuators['pmi'].pumps_get(ids='2')
    input()
    cs.robot["pmi"].set_head_config(arm=2, config=2)
    input()
    cs.robot['pmi'].set_elevator_config(arm=2, config=2)


    input()
    cs.robot['pmi'].set_elevator_config(arm=2, config=2)
    input()
    cs.robot["pmi"].goto(150, 225)
    # cs.trajman['pmi'].move_trsl(dec = 300, acc = 300, dest = 125, maxspeed = 500, sens = 1)
    input()
    cs.actuators['pmi'].pumps_drop(ids='2')
    input()
#    cs.trajman['pmi'].move_trsl(dec=300, acc=300, dest=122, maxspeed=500, sens=0)
    cs.robot["pmi"].goto(250, 225)
    input()
    cs.robot['pmi'].set_head_config(arm=2, config=0)
    input()

if __name__ == '__main__':
    test()
