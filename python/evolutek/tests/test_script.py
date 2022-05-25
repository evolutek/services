from cellaserv.proxy import CellaservProxy
from time import sleep

ROBOT = "pmi"

def home():
    cs = CellaservProxy()
    sleep(0.5)
    cs.robot[ROBOT].recalibration(x=True, y=False, y_sensor="left", init=True, side_x=True)
    input()
    cs.robot[ROBOT].goto(1830, 1130)
    input()
    cs.robot[ROBOT].goth(0)
    input()
    cs.robot[ROBOT].reverse_pattern()

home()
