#!/usr/bin/env python3

from cellaserv.proxy import CellaservProxy
from evolutek.lib.robot import Robot

from math import pi
from time import sleep

# Tools -----------------------------------------------------------------------

pal = None
pmi = None
cs = CellaservProxy()

def robot_lib(robots):
    if robots == 'both': return [pal, pmi]
    if robots == 'pal': return [pal]
    if robots == 'pmi': return [pmi]

def robot_name(robots):
    if robots == 'both': return ['pal', 'pmi']
    if robots in ['pal', 'pmi']: return [robots]

# Basic -----------------------------------------------------------------------

def translate(dest, acc, dec, maxspeed, sens, robots='both'):
    for r in robot_lib(robots):
        r.tm.move_trsl(dest, acc, dec, maxspeed, sens)

def rotate(dest, acc, dec, maxspeed, sens, robots='both'):
    for r in robot_lib(robots):
        r.tm.move_rot(dest, acc, dec, maxspeed, sens)

def move_ax(id, pos, robots='both'):
    for r in robot_name(robots):
        cs.ax["%s-%d" % (r, id)].move(goal=pos)

def cup_holder(side, action, robots='both'):
    for r in robot_name(robots):
        getattr(cs.actuators[r], '%s_cup_holder_%s' % (side, action))()

def arms(side, action, robots='both'):
    for r in robot_name(robots):
        getattr(cs.actuators[r], '%s_arm_%s' % (side, action))()

def mdb_disabled(robots='both'):
    for r in robot_lib(robots):
        r.tm.set_mdb_config(mode=3)

def mdb_loading(robots='both'):
    for r in robot_lib(robots):
        r.tm.set_mdb_config(mode=2)

def flags(action, robots='both'):
    for r in robot_name(robots):
        getattr(cs.actuators[r], 'flags_%s' % action)()

# High level ------------------------------------------------------------------

def arms_up_down(robots='both'):
    move_ax(3, 630, robots)
    move_ax(4, 630, robots)
    sleep(0.5)
    move_ax(3, 480, robots)
    move_ax(4, 480, robots)
    sleep(0.5)
    move_ax(3, 630, robots)
    move_ax(4, 630, robots)
    sleep(0.5)
    move_ax(3, 480, robots)
    move_ax(4, 480, robots)
    arms('left', 'close', robots)
    arms('right', 'close', robots)

def arms_down_up(robots='both'):
    move_ax(3, 480, robots)
    move_ax(4, 480, robots)
    sleep(0.5)
    move_ax(3, 630, robots)
    move_ax(4, 630, robots)
    sleep(0.5)
    move_ax(3, 480, robots)
    move_ax(4, 480, robots)
    sleep(0.5)
    move_ax(3, 630, robots)
    move_ax(4, 630, robots)
    arms('left', 'close', robots)
    arms('right', 'close', robots)

def activate_pumps(robots='both'):
    for r in robot_name(robots):
        for i in range(1, 5):
            cs.actuators[r].pump_get(i, 'red')

def deactivate_pumps(robots='both'):
    for r in robot_name(robots):
        for i in range(1, 5):
            cs.actuators[r].pump_drop(i)

# Main ------------------------------------------------------------------------

def dance():

    # Initial positionning:
    # Back to back in the middle of the table (pal looking to the left)
    # Pal: x=1100 y=1300, Pmi: x=1100 y=1700
    # 4 cups on the y=200 and y=2800 lines (y=900)

    deactivate_pumps()
    mdb_disabled()
    cup_holder('right', 'close')
    cup_holder('left', 'close')
    arms('right', 'close')
    arms('left', 'close')
    sleep(1)

    print("[CHORE] Arms up down")
    arms_up_down()

    print("[CHORE] Going to the edges")
    translate(500, 400, 400, 500, True)
    sleep(2)
    rotate(pi/2, 5, 5, 15, True, 'pal')
    rotate(pi/2, 5, 5, 15, False, 'pmi')
    sleep(3)

    print("[CHORE] Turning")
    mdb_loading()
    rotate(pi * 6, 5, 5, 3, True, 'pal')
    rotate(pi * 6, 5, 5, 3, False, 'pmi')
    for i in range (6):
        move_ax(3, 630)
        move_ax(4, 630)
        sleep(0.5)
        move_ax(3, 480)
        move_ax(4, 480)
        sleep(0.5)
    mdb_disabled()
    sleep(1)
    arms('right', 'close')
    arms('left', 'close')

    print("[CHORE] Turning to the buoys")
    rotate(pi/2, 5, 5, 10, False, 'pal')
    rotate(pi/2, 5, 5, 10, True, 'pmi')
    sleep(2)

    print("[CHORE] Picking up buoys")
    activate_pumps()
    translate(350, 400, 400, 500, True)
    sleep(3)
    translate(150, 300, 300, 300, True)
    sleep(3)

    print("[CHORE] Going back to center")
    rotate(pi, 5, 5, 15, True, 'pal')
    rotate(pi, 5, 5, 15, False, 'pmi')
    sleep(2)

    translate(980, 400, 400, 500, True)
    sleep(4)
    rotate(pi/2, 5, 5, 15, False, 'pal')
    rotate(pi/2, 5, 5, 15, True, 'pmi')
    sleep(2)

    print("[CHORE] Dropping buoys")
    translate(400, 400, 400, 500, True)
    sleep(4)
    deactivate_pumps()
    sleep(1)

    print("[CHORE] Going back to center")
    translate(400, 400, 400, 500, False)
    sleep(3)

    print("[CHORE] Check")
    arms('right', 'open', 'pal')
    arms('right', 'open', 'pmi')
    sleep(0.5)

    mdb_loading()
    rotate(pi, 5, 5, 15, True, 'pal')
    sleep(1.5)
    mdb_disabled()
    rotate(pi, 5, 5, 15, False, 'pal')
    sleep(0.5)
    arms('right', 'close', 'pal')
    arms('right', 'close', 'pmi')
    sleep(2)

    print("[CHORE] Pavillons")
    sleep(1)
    flags('raise');
    sleep(1)
    flags('low');


def main():

    global pal
    global pmi

    pal = Robot('pal')
    pmi = Robot('pmi')

    dance()

if __name__ == '__main__':
    main()
