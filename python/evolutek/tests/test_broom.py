from cellaserv.proxy import CellaservProxy
from time import sleep

ROBOT = "pal"

def home():
    cs = CellaservProxy()
    sleep(0.5)
    cs.robot[ROBOT].broom_square()

home()
