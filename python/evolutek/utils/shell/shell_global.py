from click_shell import shell

from cellaserv.proxy import CellaservProxy

ROBOT = None
cs = CellaservProxy()


def set_robot(robot):
    global ROBOT
    ROBOT = robot


def get_robot():
    return ROBOT
