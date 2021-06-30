from cellaserv.proxy import CellaservProxy
from math import pi

def test():
    cs = CellaservProxy()
    cs.robot['pal'].set_pos(900, 280, pi/2)
#    cs.robot['pal'].pumps_get([1, 4])
   # cs.robot['pal'].goth(1.71)i
    cs.robot['pal'].pumps_get([1, 3])
    input()
#    cs.robot['pal'].pumps_get([4, 5])
    cs.robot['pal'].goto(838.5, 1000)
    input()
    cs.robot['pal'].pumps_get([4, 5])
    cs.robot['pal'].pumps_drop([3])
    cs.robot['pal'].goto(1100, 1250)
    cs.robot['pal'].pumps_drop([5])
    cs.robot['pal'].front_arm_close()
    #cs.robot['pal'].goth(pi / 2)
    #input()
    #cs.robot['pal'].goto(850, 996)
    #input()
    #cs.robot['pal'].goth(0.85)
    #input()
    #cs.robot['pal'].goto(1111, 1214)


if __name__ == '__main__':
    test()
