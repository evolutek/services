from cellaserv.proxy import CellaservProxy
from time import sleep

ROBOT = "pmi"

def home():
    cs = CellaservProxy()
    sleep(0.5)
    cs.robot[ROBOT].recalibration(x=True, y=False, y_sensor="left", init=True, side_x=True)
    sleep(6)
    cs.robot[ROBOT].goto(1830, 1130)
    sleep(3)
    cs.robot[ROBOT].goth(0)
    sleep(1)
    cs.robot[ROBOT].reverse_pattern()

home()
