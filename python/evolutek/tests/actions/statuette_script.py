from cellaserv.proxy import CellaservProxy
from math import pi

def test():
    cs = CellaservProxy()
    cs.actuators['pmi'].pumps_get(ids='2')
    input()
    cs.robot["pmi"].set_head_config(arm=2, config=3)
    input()
    cs.robot['pmi'].set_elevator_config(arm=2, config=2)
    input()
    cs.robot['pmi'].set_elevator_config(arm=2, config=2)
    input()
    cs.robot['pmi'].set_head_config(arm=2, config=2)
    input()
    cs.trajman['pmi'].move_trsl(dec = 300, acc = 300, dest = 125, maxspeed = 500, sens = 1)
    input()
    cs.actuators['pmi'].pumps_drop(ids=2)
    input()
    cs.trajman['pmi'].move_trsl(dec=300, acc=300, dest=122, maxspeed=500, sens=0)
    input()
    cs.robot['pmi'].set_head_config(arm=2, config=0)
    input()

if __name__ == '__main__':
    test()
