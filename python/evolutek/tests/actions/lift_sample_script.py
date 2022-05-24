from cellaserv.proxy import CellaservProxy
from math import pi
from time import sleep

ROBOT = 'pal'
y = 1620
x = 340
cs: CellaservProxy = CellaservProxy()


def init_bot():
    """Initialize the bot and return the proxy object"""

    cs.trajman[ROBOT].free()
    cs.robot[ROBOT].set_pos(x=x, y=y, theta=pi/2)
    cs.trajman[ROBOT].unfree()
    print("\n\nReseting positions...\n\n")
    sleep(1)
    cs.robot[ROBOT].reset()
    cs.robot[ROBOT].set_head_config(arm=1, config=3)
    sleep(0.5)
    cs.robot[ROBOT].set_head_config(arm=2, config=1)
    sleep(0.5)
    cs.robot[ROBOT].set_head_config(arm=3, config=3)
    sleep(0.5)
    cs.actuators[ROBOT].pumps_get(ids='1')  # a enlever
    sleep(0.5)
    cs.actuators[ROBOT].pumps_get(ids='2')  # a enlever
    sleep(0.5)
    cs.actuators[ROBOT].pumps_get(ids='3')  # a enlever
    input("Initalization done !")


def test():
    init_bot()

    cs.robot[ROBOT].goto(x, y+355)
    input()
    cs.robot[ROBOT].set_elevator_config(arm=2, config=2)
    input()
    cs.robot[ROBOT].set_elevator_config(arm=2, config=0)
    input()
    cs.robot[ROBOT].goto(x, y)
    input()
    cs.actuators[ROBOT].pumps_drop(ids='2')


if __name__ == '__main__':
    test()
