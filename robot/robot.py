#!/usr/bin/env python3

from threading import Event, Thread
from time import sleep
import json
import math
import os

try:
    from pygments import highlight
    from pygments.lexers import JsonLexer
    from pygments.formatters import Terminal256Formatter
    HAVE_PYGMENTS = True
except ImportError:
    HAVE_PYGMENTS = False

from cellaserv.client import RequestTimeout
from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service
import cellaserv.settings

#import pathfinding

__doc__ = """     ##########################
     # Welcome to your robot! #
     ##########################

     Meta
         help -- This help

     Setup
         cl -- Clear serial buffer
         fq -- Flush message queue
         init -- Sends init sequence to the motor card

         free                                    //Alias : f
         unfree                                  //Alias : re

         enable                                  //Alias : e
         disable                                 //Alias : d

         fp side -- Find initial position, side is 1 or -1
         afp -- Find initial position from the config
         recal direction -- Low level recalibration, direction is 0 or 1
         debug on/off

     Move
         gotoxy x y                              //Alias: go
         gototh theta                            //Alias: gt

         mvtrsl dist acc dec maxspeed sens       //Alias: mt
         mvrot dist acc dec maxspeed sens        //Alias: mv

         curve desttr acc dec max sens destrot acc dec max sens
         stop trsldec rotdec -- Stops the robot as soon as the deceleration permits it

    Set
         setpidt P I D
         setpidr P I D

         settracc acc
         settrmax vmax
         settrdec dec

         setrotacc acc
         setrotmax vmax
         setrotdec dec

         setx x
         sety y
         sett theta

         setdeltarot theta
         setdeltatrsl mm

         setwheels diam1 diam2                   //Alias: sw
         setspacing dist

    Get
         getpidt
         getpidr
         getpos                                  //Alias: gp
         getspeeds
         getwheels
         getdelta
         getvectrsl
         getvecrot

    Interactive commands
         cws [all|spacing|diam] -- Compute wheels size
         record -- Record and replay actions
         wasd -- Control it yourself!"""


class Robot(Service):

    def __init__(self, robot=None):
        super().__init__()

        self.do_print = True

        self.cs = CellaservProxy()

        if robot is not None:
            self.tm = self.cs.trajman[robot]
        else:
            self.tm = self.cs.trajman

        # Events

        self.is_stopped = Event()
        self.robot_near_event = Event()
        self.robot_far_event = Event()
        self.robot_must_stop = Event()

        self.commands = {
            "help": self.help,

            # Setup

            "cl": self.flush_serial,
            "fq": self.flush_queue,
            "init": self.init_sequence,

            "recal": self.recalibration,
            "find_pos": self.find_position,
            "fp": self.find_position,
            "afp": self.auto_find_position,

            "-1": self.side_minus_one,
            "1": self.side_plus_one,

            "free": self.free,
            "f": self.free,
            "unfree": self.unfree,
            "re": self.unfree,

            "enable": self.enable,
            "e": self.enable,
            "disable": self.disable,
            "d": self.disable,

            "debug": self.set_debug,

            # Move

            "gotoxy": self.goto_xy,
            "go": self.goto_xy,
            "gotheta": self.goto_theta,
            "gt": self.goto_theta,

            "mvtrsl": self.move_trsl,
            "mt": self.move_trsl,
            "mvrot": self.move_rot,
            "mr": self.move_rot,

            "curve": self.curve,
            "stop": self.stop_asap,


            # Set

            "setpidt": self.set_pid_trsl,
            "setpidr": self.set_pid_rot,

            "settracc": self.set_trsl_acc,
            "settrmax": self.set_trsl_max_speed,
            "settrdec": self.set_trsl_dec,

            "setrotacc": self.set_rot_acc,
            "setrotmax": self.set_rot_max_speed,
            "setrotdec": self.set_rot_dec,

            "setx": self.set_x,
            "sety": self.set_y,
            "sett": self.set_theta,

            "setwheels": self.set_wheels_diameter,
            "sw": self.set_wheels_diameter,
            "setspacing": self.set_wheels_spacing,

            "setdeltarot": self.set_delta_rot,
            "setdeltatrsl": self.set_delta_trsl,

            # Get

            "getpidt": self.get_pid_trsl,
            "getpidr": self.get_pid_rot,
            "getpos": self.get_position,
            "gp": self.get_position,
            "getspeeds": self.get_speeds,
            "gs": self.get_speeds,
            "getwheels": self.get_wheels,
            "getdelta": self.get_delta_max,
            "getvectrsl": self.get_vector_trsl,
            "getvecrot": self.get_vector_rot,

            # Misc

            "wasd": self.wasd,
            "record": self.record,

            # Calibrate

            "computewheelssize": self.compute_wheels_size,
            "cws": self.compute_wheels_size,

        }

        self.recalibration_block = self.wrap_block(self.recalibration)
        self.goto_xy_block = self.wrap_block(self.goto_xy)
        self.goto_theta_block = self.wrap_block(self.goto_theta)
        self.curve_block = self.wrap_block(self.curve)
        self.move_rot_block = self.wrap_block(self.move_rot)
        self.move_trsl_block = self.wrap_block(self.move_trsl)

        self.goto_xy_block_avoid = self.wrap_block_avoid(self.goto_xy)
        self.goto_theta_block_avoid = self.wrap_block_avoid(self.goto_theta)
        self.move_rot_block_avoid = self.wrap_block_avoid(self.move_rot)
        self.move_trsl_block_avoid = self.wrap_block_avoid(self.move_trsl)

    def wrap_block(self, f):
        def _f(*args, **kwargs):
            self.is_stopped.clear()
            f(*args, **kwargs)
            self.is_stopped.wait()

        return _f

    def wrap_block_avoid(self, f):
        """Evitement no. 1"""
        def _f(*args, **kwargs):
            self.is_stopped.clear()
            f(*args, **kwargs)
            while not self.is_stopped.is_set():
                self.robot_must_stop.wait()
                self.cs('log.robot', is_stopped=self.is_stopped.is_set(),
                        robot_must_stop=self.robot_must_stop.is_set(),
                        robot_near=self.robot_near_event.is_set())
                if self.robot_near_event.is_set():
                    self.cs('log.robot', msg='Robot evitement')
                    self.free()
                    self.robot_far_event.wait()
                    f(*args, **kwargs)
                else:
                    break
        return _f

#    # Makes the robot go to a point avoiding obstacles.
#    # In order to decrease the computing time, coordinates are expressed in cm and not mm
#    # (this is why we have many '// 10')A
#    # We use aproximates coordinates for every point except for the last point
#    # The first point is ignored since it's the robot's position
#    def goto_with_pathfinding(self, x, y):
#        pos = self.get_position()
#        path = pathfinding.GetPath(pos['x'] // 10, pos['y'] // 10, x // 10, y // 10)
#        for i in range(1, len(path) - 1):
#            self.goto_xy_block(path[i].x * 10, path[i].y * 10)
#        self.goto_xy_block(x, y)

    ##########
    # Events #
    ##########

    @Service.event
    def robot_stopped(self):
        self.is_stopped.set()
        self.robot_must_stop.set()

    @Service.event
    def robot_near(self):
        self.robot_near_event.set()
        self.robot_must_stop.set()
        self.robot_far_event.clear()

    @Service.event
    def robot_far(self):
        self.robot_far_event.set()
        self.robot_near_event.clear()
        self.robot_must_stop.clear()

    #@Service.event
    #def robot_far(self):
    #    self.robot_far_event.set()

    def print(self, data):
        if self.do_print:
            if HAVE_PYGMENTS:
                print(highlight(json.dumps(data, sort_keys=True, indent=4),
                      JsonLexer(), Terminal256Formatter()), end='')
            else:
                print(data)

    def help(self):
        print(__doc__)

    #########
    # Setup #
    #########

    def flush_serial(self):
        self.print(self.tm.flush_serial())

    def flush_queue(self):
        self.print(self.tm.flush_queue())

    def init_sequence(self):
        self.print(self.tm.init_sequence())

    def recalibration(self, sens):
        try:
            self.print(self.tm.recalibration(sens=sens))
        except RequestTimeout: # Recalibration will timeout
            pass

    def auto_find_position(self):
        self.find_position(self.color)

    def find_position(self, c):
        color = int(c)
        self.free()
        speeds = self.get_speeds()
        self.set_theta(0)
        self.set_trsl_max_speed(200)
        self.set_trsl_acc(200)
        self.set_trsl_dec(200)
        self.set_x(1000)
        self.set_y(1000)

        print("Recalibration X")
        self.recalibration_block(0)
        print("X pos found!")
        self('beep_ok')
        sleep(1)

        self.goto_xy_block(470, 1000)
        self.goto_theta_block(math.pi / 2 * -color)

        print("Recalibration Y")
        self.recalibration_block(0)
        print("Y pos found!")
        self('beep_ok')
        sleep(1)

        self.goto_xy_block(470, 1500 + 1200 * color)
        sleep(.5)
        self.goto_xy_block(410, 1500 + 1310 * color)

        self.set_trsl_max_speed(speeds['trmax'])
        self.set_trsl_acc(speeds['tracc'])
        self.set_trsl_dec(speeds['trdec'])

        print("Setup done")
        self('beep_ready')

    def side_minus_one(self):
        self.free()
        self.set_x(94)
        self.set_y(1000)
        self.set_theta(0)

    def side_plus_one(self):
        self.free()
        self.set_x(2906)
        self.set_y(1000)
        self.set_theta(math.pi)

    def set_debug(self, state):
        self.print(self.tm.set_debug(state=state))

    ########################
    # Un/Free (En/Dis)able #
    ########################

    def free(self):
        self.print(self.tm.free())

    def unfree(self):
        self.print(self.tm.unfree())

    def enable(self):
        self.print(self.tm.enable())

    def disable(self):
        self.print(self.tm.disable())


    ########
    # Move #
    ########

    def goto_xy(self, x, y):
        self.print(self.tm.goto_xy(x=x, y=y))

    def goto_theta(self, theta):
        self.print(self.tm.goto_theta(theta=theta))

    def move_trsl(self, dest, acc, dec, maxspeed, sens):
        self.print(self.tm.move_trsl(dest=dest, acc=acc, dec=dec,
            maxspeed=maxspeed, sens=sens))

    def move_rot(self, dest, acc, dec, maxspeed, sens):
        self.print(self.tm.move_rot(dest=dest, acc=acc, dec=dec,
            maxspeed=maxspeed, sens=sens))

    def curve(self, dt, at, det, mt, st, dr, ar, der, mr, sr, delayed):
        self.print(self.tm.curve(dt=dt, at=at, det=det, mt=mt, st=st, dr=dr,
            ar=ar, der=der, mr=mr, sr=sr, delayed=delayed))

    def stop_asap(self, trsldec, rotdec):
        self.print(self.tm.stop_asap(trsldec=trsldec, rotdec=rotdec))

    #######
    # Set #
    #######

    def set_pid_trsl(self, P, I, D):
        self.print(self.tm.set_pid_trsl(P=P, I=I, D=D))

    def set_pid_rot(self, P, I, D):
        self.print(self.tm.set_pid_rot(P=P, I=I, D=D))

    def set_trsl_acc(self, acc):
        self.print(self.tm.set_trsl_acc(acc=acc))

    def set_trsl_max_speed(self, maxspeed):
        self.print(self.tm.set_trsl_max_speed(maxspeed=maxspeed))

    def set_trsl_dec(self, dec):
        self.print(self.tm.set_trsl_dec(dec=dec))

    def set_rot_acc(self, acc):
        self.print(self.tm.set_rot_acc(acc=acc))

    def set_rot_max_speed(self, maxspeed):
        self.print(self.tm.set_rot_max_speed(maxspeed=maxspeed))

    def set_rot_dec(self, dec):
        self.print(self.tm.set_rot_dec(dec=dec))

    def set_x(self, x):
        self.print(self.tm.set_x(x=x))

    def set_y(self, y):
        self.print(self.tm.set_y(y=y))

    def set_theta(self, theta):
        self.print(self.tm.set_theta(theta=theta))

    def set_wheels_diameter(self, w1, w2):
        self.print(self.tm.set_wheels_diameter(w1=w1, w2=w2))

    def set_wheels_spacing(self, spacing):
        self.print(self.tm.set_wheels_spacing(spacing=spacing))

    def set_delta_rot(self, theta):
        self.print(self.tm.set_delta_max_rot(delta=theta))

    def set_delta_trsl(self, mm):
        self.print(self.tm.set_delta_max_trsl(delta=mm))

    #######
    # Get #
    #######

    def get_pid_trsl(self):
        ret = self.tm.get_pid_trsl()
        self.print(ret)
        return ret

    def get_pid_rot(self):
        ret = self.tm.get_pid_rot()
        self.print(ret)
        return ret

    def get_position(self):
        ret = self.tm.get_position()
        self.print(ret)
        return ret

    def get_speeds(self):
        ret = self.tm.get_speeds()
        self.print(ret)
        return ret

    def get_wheels(self):
        ret = self.tm.get_wheels()
        self.print(ret)
        return ret

    def get_delta_max(self):
        ret = self.tm.get_delta_max()
        self.print(ret)
        return ret

    def get_vector_trsl(self):
        ret = self.tm.get_vector_trsl()
        self.print(ret)
        return ret

    def get_vector_rot(self):
        ret = self.tm.get_vector_rot()
        self.print(ret)
        return ret

    ###############
    # Interactive #
    ###############

    def up(self, step):
        pos = self.tm.get_position()
        self.goto_xy_block(x=pos['x'], y=pos['y']+step)

    def down(self, step):
        self.up(-step)

    def right(self, step):
        pos = self.tm.get_position()
        self.goto_xy_block(x=pos['x']+step, y=pos['y'])

    def left(self, step):
        self.right(-step)

    def rotate(self, step):
        pos = self.tm.get_position()
        self.goto_theta_block(theta=pos['theta']+step)

    def wasd(self):
        STEP = 200
        STEP_ANGLE = math.pi / 2

        self.do_print = False

        import curses
        stdscr = curses.initscr()
        curses.noecho()
        while True:
            c = stdscr.getch()
            if c == 27: # Escape
                break
            elif chr(c) == 'w':
                self.up(STEP)
            elif chr(c) == 's':
                self.down(STEP)
            elif chr(c) == 'a':
                self.left(STEP)
            elif chr(c) == 'd':
                self.right(STEP)
            elif chr(c) == 'q':
                self.rotate(STEP_ANGLE)
            elif chr(c) == 'e':
                self.rotate(-STEP_ANGLE)
            elif chr(c) == '1':
                self.cs.actuators.collector_open()
            elif chr(c) == '2':
                self.cs.actuators.collector_close()
            elif chr(c) == '3':
                self.cs.actuators.collector_hold()

        curses.echo()
        curses.endwin()
        self.do_print = True

    def record(self):
        import record

        self.free()

        print("Welcome to the record subshell!")
        print("""
    kp -- record a key position
    kt -- record a key theta
    @service.action args... -- record a key action

    Precede a move command with '!' to make it unblocking

    list -- list keys
    delete %d -- delete a key

    replay -- replay keys
    save name -- save to service 'name'
    quit
""")
        keys = []

        while True:
            msg = input("{:2}: ".format(len(keys))).strip()

            if not msg:
                continue

            if msg == 'kp':
                block = not msg.startswith('!')
                pos = self.tm.get_position()
                keys.append(record.KeyPosition(self, self.cs, block,
                                               pos['x'], pos['y']))

            elif msg == 'kt':
                block = not msg.startswith('!')
                pos = self.tm.get_position()
                keys.append(record.KeyTheta(self, self.cs, block,
                                            pos['theta']))

            elif msg.startswith('@'):
                key_action = record.KeyAction(self, self.cs, msg[1:])
                key_action()
                keys.append(key_action)

            elif 'list'.startswith(msg):
                for i, key in enumerate(keys):
                    print("{:2}: {}".format(i, key))

            elif msg.startswith('save'):
                name = msg.split()[1]
                filename = name + '.py'

                A = ''
                for key in keys:
                    A += ' ' * 8 + repr(key) + '\n'

                with open(filename, "w") as f:
                    f.write(record.TEMPLATE_KEY_IA.format(name=name, keys=A))

                import os
                import stat
                st = os.stat(filename)
                os.chmod(filename, st.st_mode | stat.S_IEXEC)

                print("You can now run ./{}".format(filename))
                print("It will wait for the event '{}-start'".format(name))

            elif 'replay'.startswith(msg):
                for key in keys:
                    key()
                self.free()

            elif msg.startswith('delete'):
                del keys[int(msg.split()[1])]

            elif 'quit'.startswith(msg):
                return

    @Service.thread
    def loop(self):
        if __name__ != '__main__':
            return

        print(__doc__)

        # XXX: Warning
        self.flush_serial()

        while True:
            try:
                s = input('<< ')
                if not s:
                    continue
                words = s.split()
                if words[0] in self.commands:
                    self.commands[words[0]](*words[1:])
                else:
                    print("Command not found.")
            except (KeyboardInterrupt, EOFError):
                    os.kill(os.getpid(), 9)
            except Exception as e:
                print(e)

    def compute_wheels_size(self, arg):
        self.free()
        print("###############################################################")
        print("## Hi ! and welcome to the wheels size computing assistant ! ##")
        print("###############################################################")
        print("Please place the robot on a special mark, facing the right direction. Press enter when ready")
        input()
        self.set_x(1000)
        self.set_y(1000)
        self.set_theta(0)
        sleep(.1)
        old = self.get_wheels()
        sleep(.1)
        speeds = self.get_speeds()
        sleep(.1)
        if arg == "all" or arg == "diam":
            print("########################################################")
            print("Please enter the length of the distance to mesure (mm) :")
            print("########################################################")
            length = float(input())
            print("Length = ", length)
            print("Getting the old settings...")
            self.set_trsl_max_speed(100)
            sleep(.1)
            print("################################################################")
            print("Do you want the robot to go to the second mark by itself (y/n) ?")
            print("################################################################")
            if input()[0] == 'y':
                print("Going...")
                self.goto_xy_block(1000 + length, 1000)
            sleep(.1)
            self.free()
            print("#################################################################")
            print("Please place the robot on the second mark, press Enter when ready")
            print("#################################################################")
            input()
            newpos = self.get_position()
            #mesured = ((newpos[0] - 1000) ** 2 + (newpos[1] - 1000) ** 2))
            mesured = (newpos['x'] - 1000)
            coef = float(length) / float(mesured)
            coef1 = float(length)\
                / float(mesured - math.sin(newpos['theta']) * old['spacing'])
            coef2 = float(length)\
                / float(mesured + math.sin(newpos['theta']) * old['spacing'])
            print("The error was of :", length - (newpos['x'] - 1000))
            print("The new diameters are :", old['left_diameter'] * coef,
                    old['right_diameter'] * coef)
            print("Setting the new diameters")
            self.set_wheels_diameter(old['left_diameter'] * coef,
                    old['right_diameter'] * coef)
            sleep(.1)
            print("########################")
            print("Going back to the origin")
            print("########################")
            self.set_x(1000 + length)
            self.set_theta(0)
            self.goto_xy_block(1000, 1000)
            self.free()
        if arg == "all" or arg == "spacing":
            print("##########################################")
            print("Please enter the number of turns to mesure")
            print("##########################################")
            nbturns = float(input())
            print("nbturns = ", nbturns)
            nbturns = nbturns * 2
            print("#######################################################")
            print("Do you want the robot to do the turns by itself (y/n) ?")
            print("#######################################################")
            if input()[0] == 'y':
                print("Going...")
                self.move_rot_block(nbturns * math.pi, 3, 3, 3, 1)
                sleep(.1)
                self.free()
                print("############################################################")
                print("Please replace the robot on the mark, press Enter when ready")
                print("############################################################")
            else:
                print("################################################################")
                print("Please make the robot do turns on itself, press Enter when ready")
                print("################################################################")
            input()
            newpos = self.get_position()
            mesured = newpos['theta'] + nbturns * math.pi
            coef = float(mesured) / float(nbturns * math.pi)
            print("The error was of :", newpos['theta'])
            print("The new spacing is :", old['spacing'] * coef)
            print("Setting the new spacing")
            self.set_wheels_spacing(old['spacing'] * coef)
            self.set_theta(0)
            self.move_rot_block(nbturns * math.pi, 3, 3, 3, 0)
        self.set_trsl_max_speed(speeds['trmax'])
        print("#############################################")
        print("## GO TO THE MOTOR CARD AND SET THE VALUES ##")
        print("#############################################")
        print(self.get_wheels())

def main():
    try:
        import readline
    except ImportError:
        print("You don't have readline, too bad for you...")

    robot_cellaserv = cellaserv.settings.ROBOT
    robot = Robot(robot_cellaserv)
    robot.run()

if __name__ == "__main__":
    main()
