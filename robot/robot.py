#!/usr/bin/env python3

import math
import json
from threading import Event, Thread
from time import sleep

try:
    from pygments import highlight
    from pygments.lexers import JsonLexer
    from pygments.formatters import Terminal256Formatter
    HAVE_PYGMENTS = True
except ImportError:
    HAVE_PYGMENTS = False

from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service

# TODO: Robot bacon (Pilipe!)

__doc__ = \
"""     ##########################
     # Welcome to your robot! #
     ##########################

     Meta
         help -- This help

     Setup
         cl -- Clear serial buffer
         fq -- Flush message queue

         free                                    //Alias : f
         unfree                                  //Alias : re

         fp side -- Find initial position, side is 1 or -1
         recal direction -- Low level recalibration, direction is 0 or 1
         debug on/off

     Move
         gotoxy x y                              //Alias: go
         gototh theta                            //Alias: gt

         mvtrsl dist acc dec maxspeed sens       //Alias: mt
         mvrot dist acc dec maxspeed sens        //Alias: mv

         curve desttr acc dec max sens destrot acc dec max sens

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

         setwheels diam1 diam2                   //Alias: sw
         setspacing dist

    Get
         getpidt
         getpidr
         getpos                                  //Alias: gp
         getspeeds
         getwheels

    Interactive commands
         cws [all|spacing|diam] -- Compute wheels size
         record -- Record and replay actions
         wasd -- Control it yourself!"""

class Robot(Service):

    def __init__(self):
        super().__init__()

        self.do_print = True

        self.cs = CellaservProxy()
        self.tm = self.cs.trajman

        # Events

        self.is_stopped = Event()
        self.robot_near_event = Event()

        self.commands = {
            "help": self.help,

            # Setup

            "cl": self.flush_serial,
            "fq": self.flush_queue,

            "recal": self.recalibration,
            "find_pos": self.find_position,
            "fp": self.find_position,

            "-1": self.side_minus_one,
            "1": self.side_plus_one,

            "free": self.free,
            "f": self.free,
            "unfree": self.unfree,
            "re": self.unfree,

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

            # Get

            "getpidt": self.get_pid_trsl,
            "getpidr": self.get_pid_rot,
            "getpos": self.get_position,
            "gp": self.get_position,
            "getspeeds": self.get_speeds,
            "gs": self.get_speeds,
            "getwheels": self.get_wheels,

            "wasd": self.wasd,
            "record": self.record,
#            "computewheelssize": compute_wheels_size,
#            "cws": compute_wheels_size,

        }

        self.recalibration_block = self.wrap_block(self.recalibration)
        self.goto_xy_block = self.wrap_block(self.goto_xy)
        self.goto_theta_block = self.wrap_block(self.goto_theta)
        self.curve_block = self.wrap_block(self.curve)

    def wrap_block(self, f):
        def _f(*args, **kwargs):
            self.is_stopped.clear()
            f(*args, **kwargs)
            self.is_stopped.wait()

        return _f
    ##########
    # Events #
    ##########

    @Service.event
    def robot_stopped(self):
        self.is_stopped.set()

    @Service.event
    def robot_near(self):
        self.robot_near_event.set()

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

    def recalibration(self, sens):
        try:
            self.print(self.tm.recalibration(sens=sens))
        except: # Recalibration will timeout
            pass

    def find_position(self, c):
        """ c = -1 (blue) or c = 1 (red) """
        color = int(c)
        self.free()
        self.set_theta(math.pi / 2.0)
        self.set_trsl_max_speed(200)
        self.set_x(1000)
        self.set_y(1000)

        print("Recalibration Y")
        self.recalibration_block(0)
        sleep(.1)
        self.flush_queue()
        print("Stopped")
        print("Y pos found!")

        self.goto_xy_block(1000, 1000)
        self.goto_theta_block(math.pi / 2.0 + math.pi / 2.0 * color)

        print("Recalibration X")
        self.recalibration_block(0)
        sleep(.1)
        self.flush_queue()
        print("X pos found!")

        self.goto_xy_block(1500 + 1100 * color, 1000)
        self.set_trsl_max_speed(100)
        self.goto_xy_block(1500 + 1500 * color - 185 / 2.0 * color, 1000)
        self.set_trsl_max_speed(800)
        print("Setup done")

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

    ###########
    # Un/Free #
    ###########

    def free(self):
        self.print(self.tm.free())

    def unfree(self):
        self.print(self.tm.unfree())

    ########
    # Move #
    ########

    def goto_xy(self, x, y):
        self.print(self.tm.goto_xy(x=x, y=y))

    def goto_theta(self, theta):
        self.print(self.tm.goto_theta(theta=theta))

    def move_trsl(self, dest, acc, dec, maxspeed, sens):
        self.print(self.tm.move_trsl(dest=dest, acc=acc, dec=dec,
            maxspeed=maxpseed, sens=sens))

    def move_rot(self, dest, acc, dec, maxspeed, sens):
        self.print(self.tm.move_rot(dest=dest, acc=acc, dec=dec,
            maxspeed=maxspeed, sens=sens))

    def curve(self, dt, at, det, mt, st, dr, ar, der, mr, sr, delayed):
        self.print(self.tm.curve(dt=dt, at=at, det=det, mt=mt, st=st, dr=dr,
            ar=ar, der=der, mr=mr, sr=sr, delayed=delayed))

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

    #######
    # Get #
    #######

    def get_pid_trsl(self):
        self.print(self.tm.get_pid_trsl())

    def get_pid_rot(self):
        self.print(self.tm.get_pid_rot())

    def get_position(self):
        self.print(self.tm.get_position())

    def get_speeds(self):
        self.print(self.tm.get_speeds())

    def get_wheels(self):
        self.print(self.tm.get_wheels())

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

        elf.free()

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
                print("It will wait for the event '{}-start'".format(name.replace('_', '-')))

            elif 'replay'.startswith(msg):
                for key in keys:
                    key()
                self.free()

            elif msg.startswith('delete'):
                del keys[int(msg.split()[1])]

            elif 'quit'.startswith(msg):
                return

    def loop(self):
        print(__doc__)

        # XXX: Warning
        self.flush_serial()

        while True:
            try:
                s = input('>> ')
                if not s:
                    continue
                words = s.split()
                if words[0] in self.commands:
                    self.commands[words[0]](*words[1:])
                else:
                    print("Command not found.")
            except Exception as e:
                print(e)

def main():
    try:
        import readline
    except ImportError:
        print("You don't have readline, too bad for you...")

    robot = Robot()
    thread_loop = Thread(target=robot.loop)
    thread_loop.start()
    robot.run()

if __name__ == "__main__":
    main()

