from cellaserv.proxy import CellaservProxy
from math import pi

def test():
    cs = CellaservProxy()
    cs.robot['pal'].set_pos(940, 280, pi/2)
    cs.robot['pal'].pumps_get([1, 4])
    input()
    cs.robot['pal'].goth(1.71)
    input()
    cs.robot['pal'].goto(882, 507)
    input()
    cs.robot['pal'].goth(pi / 2)
    input()
    cs.robot['pal'].goto(880, 996)
    input()
    cs.robot['pal'].goth(0.85)
    input()
    cs.robot['pal'].goto(1111, 1214)


if __name__ == '__main__':
    test()
