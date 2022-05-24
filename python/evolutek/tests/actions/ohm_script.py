from cellaserv.proxy import CellaservProxy
from math import pi
from time import sleep

ROBOT = "pmi"
cs: CellaservProxy = CellaservProxy()


def test():
    cs.trajman[ROBOT].free()
    cs.robot[ROBOT].set_pos(x=1800, y=1130, theta=0)
    cs.trajman[ROBOT].unfree()

    cs.robot[ROBOT].set_elevator_config(arm=1, config=0)
    input()
    cs.robot[ROBOT].set_elevator_config(arm=3, config=0)
    input()
    cs.robot[ROBOT].set_elevator_config(arm=2, config=0)
    input()
    cs.robot[ROBOT].goto(1910, 1130)
    input()
    cs.trajman[ROBOT].move_trsl(10, 150, 150, 100, 1)
    input()
    cs.robot[ROBOT].set_elevator_config(arm=1, config=4)
    input()
    cs.robot[ROBOT].set_elevator_config(arm=3, config=4)
    input()
    cs.robot[ROBOT].pattern = cs.robot[ROBOT].get_pattern()
    print(cs.robot[ROBOT].pattern)
    input()
    cs.robot[ROBOT].set_elevator_config(arm=1, config=0)
    input()
    cs.robot[ROBOT].set_elevator_config(arm=3, config=0)
    input()
    cs.trajman[ROBOT].move_trsl(10, 150, 150, 100, 0)
    input()
    cs.robot[ROBOT].goto(1800, 1130)

def action2():
    cs.robot[ROBOT].goth(theta = -pi/2)
    input()
    y = 1777.5
    if(cs.robot[ROBOT].pattern == 1 or cs.robot[ROBOT].pattern == 4):
        y = 1670
        print("purple")
    else:
        print("yellow")
    while(cs.trajman[ROBOT].get_position().y != y):
        cs.robot[ROBOT].goto(1800, y)
    # input()
    # cs.robot[ROBOT].goto(1800, y)
    input()
if __name__ == '__main__':
    test()
    action2()
