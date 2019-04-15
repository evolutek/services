from cellaserv.proxy import CellaservProxy
from evolutek.lib.settings import ROBOT
from time import sleep



cs = CellaservProxy()
trajman = cs.trajman[ROBOT]

def waitmove():
    done = False
    while trajman.is_moving():
        sleep(.1)
    print(trajman.get_position())
    


trajman.set_x(0)
trajman.set_y(0)
trajman.set_theta(0)
for a in range(10):
    trajman.goto_xy(x=300, y=0)
    waitmove()
    trajman.goto_xy(x=300, y=300)
    waitmove()
    trajman.goto_xy(x=0, y=300)
    waitmove()
    trajman.goto_xy(x=0,y=0)
    waitmove()
trajman.goto_theta(0)
