from cellaserv.proxy import CellaservProxy
from math import pi
from time import sleep

ROBOT = "pmi"
cs: CellaservProxy = CellaservProxy()
Pattern= -1

def test():
    global Pattern
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
    Pattern = cs.robot[ROBOT].get_pattern()
    print(Pattern)
    input()
    cs.robot[ROBOT].set_elevator_config(arm=1, config=0)
    input()
    cs.robot[ROBOT].set_elevator_config(arm=3, config=0)
    input()
    cs.trajman[ROBOT].move_trsl(10, 150, 150, 100, 0)
    input()
    cs.robot[ROBOT].goto(1800, 1130)

def action2():
    print((cs.trajman[ROBOT].get_position()))
    print(cs.robot[ROBOT].goth(theta = -1.57))
    sleep(5)
    print((cs.trajman[ROBOT].get_position()))
    y = 1777.5
    print(f"alalal mon pattern c'est {Pattern}")

    if(Pattern == 1 or Pattern == 4):
        y = 1592.5
        print("purple")
    else:
        print("yellow")
    print(f"alalal mon y est {y}")
    
    print(cs.robot[ROBOT].goto(1830, y))
    # input()
    # cs.robot[ROBOT].goto(1800, y)
    input()

def tests():
    pattern = Pattern - 1
    patterns = [
            [True, True, False, False, True, True, False],
            [False, True, True, True, False, False, True],
            [True, True, False, True, False, False, True],
            [False, True, True, False, True, True, False]
            ]
    if pattern in [0, 3]:
        plot = 5
    else:
        plot = 6
    while cs.trajman[ROBOT].get_position()['y'] > 680:
        if patterns[pattern][plot]:
            cs.robot[ROBOT].left_arm_open()
            input()
            cs.robot[ROBOT].left_arm_close()
            input()
        plot -= 1
        cs.robot[ROBOT].goto(1830, cs.trajman[ROBOT].get_position()['y']-185)
        input()
    if patterns[pattern][plot]:
        cs.robot[ROBOT].left_arm_open()
        input()
        cs.robot[ROBOT].left_arm_close()


if __name__ == '__main__':
    print("TEST")
    test()
    print("ACTION2")
    action2()
    print("TESTS")
    tests()
