from cellaserv.proxy import CellaservProxy
from math import pi
from time import sleep


def test():
    cs: CellaservProxy = CellaservProxy()
    cs.robot['pmi'].set_pos(x=400, y=820, theta=pi)

# Dépôt inférieur

    cs.robot['pmi'].set_elevator_config(arm=1, config=2)
    input()
    cs.robot['pmi'].set_elevator_config(arm=2, config=2)
    input()
    cs.robot['pmi'].set_elevator_config(arm=3, config=2)
    input()
    cs.robot['pmi'].set_head_config(arm=1, config=3)
    input()
    cs.robot['pmi'].set_head_config(arm=2, config=3)
    input()
    cs.robot['pmi'].set_head_config(arm=3, config=3)
    input()
    # cs.actuators['pmi'].pumps_get(ids=1)
    # input()
    # cs.actuators['pmi'].pumps_get(ids=2)
    # input()
    # cs.actuators['pmi'].pumps_get(ids=3)
    # input()
    cs.trajman['pmi'].move_trsl(dest=240, acc=300, dec=300, maxspeed=200, sens=1)
    input()
    cs.actuators['pmi'].pumps_drop(ids=1)
    input()
    cs.actuators['pmi'].pumps_drop(ids=2)
    input()
    cs.actuators['pmi'].pumps_drop(ids=3)
    input()
    cs.trajman['pmi'].move_trsl(dest=240, acc=300, dec=300, maxspeed=200, sens=0)
    input()


if __name__ == '__main__':
    test()
