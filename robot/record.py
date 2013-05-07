TEMPLATE_KEY_IA = """#!/usr/bin/env python3
from threading import Thread, Event

from cellaserv.service import Service
from cellaserv.proxy import CellaservProxy
from robot import Robot

class {name}(Service):

    def __init__(self):
        super().__init__()

        self.cs = CellaservProxy()

        self.start_event = Event()

        self.robot = Robot()
        self.robot.setup()

    @Service.event
    def {name}_start(self):
        self.start_event.set()

    def start(self):
        self.start_event.wait()

{keys}

def main():
    service = {name}()
    service.setup()

    service_thread = Thread(target=service.start)
    service_thread.start()

    Service.loop()

if __name__ == '__main__':
    main()
"""

class Key:
    def __init__(self, robot, cs):
        self.robot = robot
        self.cs = cs

    def __repr__(self):
        """Python form"""
        pass

    def __call__(self):
        eval(repr(self))

class KeyPosition(Key):

    def __init__(self, robot, cs, block, x, y):
        super().__init__(robot, cs)

        self.block = block
        self.x = x
        self.y = y

    def __repr__(self):
        return "self.robot.goto_xy_{}(x={x}, y={y})".format(
                'block' if self.block else '', x=self.x, y=self.y)

class KeyTheta(Key):

    def __init__(self, robot, cs, block, theta):
        super().__init__(robot, cs)

        self.block = block
        self.theta = theta

    def __repr__(self):
        return "self.robot.goto_theta_{}(theta={theta})".format(
                'block' if self.block else '', theta=self.theta)

class KeyAction(Key):

    def __init__(self, robot, cs, eval):
        super().__init__(robot, cs)

        self.eval = eval

    def __repr__(self):
        return "self.cs.{}".format(self.eval)
