from cellaserv.proxy import CellaservProxy
from math import pi

def test():
    cs = CellaservProxy()
    cs.robot['pal'].recalibration(y = True, x = False, x_sensor = "right")
    input()
    cs.robot['pal'].goto(1640, 250)
    input()
    cs.robot['pal'].goto(1700, 300)
    input()
    cs.robot['pal'].goth(3 * pi / 4)
    input()
    cs.robot['pal'].goto(1825, 175)
    input()
    cs.robot['pal'].goth(pi / 2)
    #input()
   # cs.robot['pal'].recalibration(y = True, x = False, x_sensor = "right")
    input()
    cs.robot['pal'].push_windsocks()

if __name__ == '__main__':
    test()
