#!/usr/bin/env python3

from cellaserv.service import Service, ConfigVariable
from cellaserv.proxy import CellaservProxy
from math import pi
from time import sleep
from threading import Thread, Timer, Event

from evolutek.lib.objectives import get_strat

@Service.require("trajman", "pal")
@Service.require("actuators", "pal")
@Service.require("map", "pal")
@Service.require("tirette")
class Ai(Service):
    """
    Class representing the decision taking by the robot durint a match
    """
    # Init of the PAL
    def __init__(self):
        print("Init")
        super().__init__('pal')
        self.cs = CellaservProxy()
        self.trajman = self.cs.trajman['pal']
        self.gbts = self.cs.gbts['pal']
        self.actuators = self.cs.actuators['pal']
        self.map = self.cs.map['pal']

        self.gbts.set_avoiding(False)
        self.color = self.cs.config.get(section='match', option='color')

        # Set Timer
        self.stop_timer = Timer(98, self.match_stop)
        # Thread for the match
        self.match_thread = Thread(target=self.start)

        # Stopped event
        self.front_stopped = Event()
        self.back_stopped = Event()
        self.moving_side = 0.0

        # All objectives
        self.objectives = get_strat(self.color, self.actuators)
        self.position = 'start'

        # Setup Trajman
        self.setup()

    # Setup PAL position
    def setup(self):
        """
          Sets up values before a match
        """
        print("Setup")
        self.trajman.free()
        self.trajman.set_x(500)
        self.trajman.set_y(240 if self.color == 'green' else 2760)
        self.trajman.set_theta(pi/2 if self.color == 'green' else -pi/2)
        self.trajman.unfree()
        self.actuators.init_all()
        print("Setup complete, waiting to receive match_start")

    # Starting of the match
    @Service.eventi
    def match_start(self):
        """
          Starts a match
         """
        print("Go")
        self.stop_timer.start()
        self.gbts.set_avoiding(True)
        print("Gas Gas Gas")
        self.match_thread.start()

    # Ending of the match
    def match_stop(self):
        """
          Ends a match
         """
        print("Stop")
        self.trajman['pal'].free()
        self.trajman['pal'].disable()
        quit()

    # Avoid front obstacle
    @Service.event
    def front_avoid(self):
        """
          Enters "avoiding" state
        """
        print('Front detection')
        print('moving_side: ' + str(self.moving_side))
        if self.moving_side > 0.0:
            print("Avoid")
            self.trajman['pal'].stop_asap(1000, 30)
            self.front_stopped.set()

    # Avoid back obstacle
    @Service.event
    def back_avoid(self):
        """
          Leaves "avoiding" state
        """
        print('Back detection')
        print('moving_side: ' + str(self.moving_side))
        if self.moving_side < 0.0:
            print("Avoid")
            self.trajman['pal'].stop_asap(1000, 30)
            self.back_stopped.set()

    @Service.event
    def front_end_avoid(self):
        """
          Enters "avoiding" state
        """
        print("Front end avoid")
        self.front_stopped.clear()

    @Service.event
    def back_end_avoid(self):
        """
          Leaves "avoiding" state
        """
        print("Back end avoid")
        self.back_stopped.clear()

    def manage_tasks(self, tasks):
        """
          Executes one by one the tasks and deplete them.
        """
        while not tasks.empty():
            sleep(1)

            # New task
            curr_task = tasks.get()
            if not curr_task:
                break

            if curr.speed:
                self.set_speed(curr.speed)

            if curr_task.not_avoid:
                self.front_stopped.clear()
                self.back_stopped.clear()
                self.gbts.set_avoiding(False)
            else:
                self.gbts.set_avoiding(True)

            while True:
                sleep(1)
                self.goto_xy(curr_task.x, curr_task.y)
                if not (self.front_stopped.isSet() or self.back_stopped.isSet()):
                    break

            # We can rotate
            if curr_task.theta:
                self.goto_theta(curr_task.theta)

            # We can do an action
            if curr_task.action:
                if curr_task.action_param:
                    curr_task.action(curr_task.action_param)
                else:
                    curr_task.action()

        # Finish to manage all tasks of the objective
        print('End of the tasks for this objective')
        self.gbts.set_avoiding(True)

    # Start of the match
    def start(self):
        """
          Start a match and executes tasks until all of them are finished
        """
        print("Starting the match")


        while not self.objectives.empty():
            sleep(1)

            print('Get a new objective')
            # New objective
            curr_objective = self.objectives.get()
            # No new objective
            if not curr_objective:
                break

            # goto pathfinding
            self.goto_xy_with_pathfinding(curr_objective.destination)
            self.positon = curr_objective.destination[0]

            # Manage tasks of the objective
            self.manage_tasks(curr_objectives.tasks)

            # go to the ending point
            ending = self.curr_objectives.ending
            ending_point = self.map.get_coords(ending)
            while True:
                sleep(1)
                self.goto_xy(ending_point['x'], ending_point['y'])
                if not (self.front_stopped.isSet() or self.back_stopped.isSet()):
                    break
            self.positon = ending[0]

        # We have done all our tasks
        print("Match is finished")

    # Go to x y position
    def goto_xy(self, x, y):
        """
          Tells the robot to get a new position at x,y
        """

        self.trajman.goto_xy(x=x, y=y)
        self.moving_side = self.trajman.get_vector_trsl()['trsl_vector']
        while self.trajman.is_moving():
            print('Moving')
            sleep(0.5)
        self.moving_side = 0.0

    def goto_xy_with_pathfinding(self, destination):
        """
          Tells the robot to travel to the destination by taking the shortest
          path on the map
        """
        path = []
        print('Trying to search for a path')
        while path == []:
            path = self.map.get_path(self.position, destination)
            sleep(1)
        print("Path: " + str(path))
        for i in range(1, len(path)):
            next = path[i][1]
            print('Going to move to the point: ' + path[i])
            while True:
                sleep(1)
                self.goto_xy(next['x'], next['y'])
                if not (self.front_stopped.isSet() or self.back_stopped.isSet()):
                    break
        print('Finish the path')

    # Do a movement in tranlation
    def move_trsl(self, len):
        """
          Moves robot with a translation movement
        """
        self.trajman.move_trsl(len, 10, 10, 10, 0)
        while self.trajman.is_moving():
            continue

    # Go to theta
    def goto_theta(self, theta):
        """
          Sets the rotation of the robot
        """
        self.trajman.goto_theta(theta=theta)
        while self.trajman.is_moving():
            continue

    # Set max speed
    def set_speed(self, speed):
        """
          modifies de robot's speed
        """
        self.trajman.set_trsl_max_speed(speed)

def main():
    ai = Ai()
    ai.run()

if __name__  == '__main__':
    main()
