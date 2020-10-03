from cellaserv.proxy import CellaservProxy
from evolutek.lib.robot import Robot
from evolutek.lib.gpio import Gpio, Edge



from sys import argv
from math import pi

"""
set la position du robot
attendre que la tirette soit tirée
l'ia nous dirigeras vers une position x
push les windsocks
"""

cs = CellaservProxy()
ROBOT = None
robot = None

def homologation():
    if ROBOT == 'pal':
        cs.tm.set_pos(640, 120, pi / 2, True)
    else :
        cs.tm.set_pos(950, 120, pi / 2, True)
    tirette = Gpio(17, "tirette", False, edge=Edge.FALLING)
    while tirette.read() == 0:
        continue
    cs.actuators[ROBOT]._windsocks_push()
    


def main():
    selected_robot = argv[1]
    if not selected_robot in ['pal', 'pmi']:
        print("select a valid robot")
        return

    global ROBOT
    ROBOT = selected_robot
    global robot
    robot = Robot(selected_robot)
    homologation()

if __name__ == "__main__":
    main()