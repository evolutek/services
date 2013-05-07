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

try:
    import readline
except ImportError:
    print("You don't have readline, too bad for you...")

from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service

__doc__ = \
"""     ############################################
     Bienvenue dans le shell de la carte moteur !
     ############################################
     Les commandes disponibles sont les suivantes :
         gotoxy x y                              //Alias : go
         gototh theta                            //Alias : gt
         mvtrsl dist acc dec maxspeed sens
         mvrot dist acc dec maxspeed sens
         free                                    //Alias : f
         recal sens
         unfree                                  //Alias : re
         setpidt P I D
         setpidr P I D
         debug on/off
         settracc acc
         settrmax vmax
         settrdec dec
         setrotacc acc
         setrotmax vmax
         setrotdec dec
         setx x
         sety y
         sett theta
         getpidt
         getpidr
         getpos                                  //Alias : gp
         getspeeds
         courbe desttr acc dec max sens destrot acc dec max sens
         help
         cl
         fp
         setwheels diam1 diam2                   //Alias : sw
         setspacing dist
         getwheels
         cws [all|spacing|diam] //Calculate wheels size
         w a s d"""

class Shell(Service):

    def __init__(self):
        super().__init__()

        self.do_print = True

        self.cs = CellaservProxy()
        self.tm = self.cs.trajman

        self.is_stopped = Event()

        self.commands = {
            # Setup

            "cl": self.flush_serial,
            "fq": self.flush_queue,
            "help": self.help,

            "recal": self.recalibration,
            "find_pos": self.find_position,
            "fp": self.find_position,

#            "computewheelssize": compute_wheels_size,
#            "cws": compute_wheels_size,

            # Move

            "gotoxy": self.goto_xy,
            "go": self.goto_xy,
            "gotheta": self.goto_theta,
            "gt": self.goto_theta,
            "mvtrsl": self.move_trsl,
#            "mt": MoveTrsl,
#            "mvrot": MoveRot,
#            "mr": MoveRot,
            "free": self.free,
            "f": self.free,
            "unfree": self.unfree,
            "re": self.unfree,
#            "curve": Curve,
#            "courbe": Courbe,

            # Set

#            "setpidt": SetPIDTrsl,
#            "setpidr": SetPIDRot,
#            "debug": SetDebug,
#            "settracc": SetTrslAcc,
#            "settrmax": SetTrslMaxSpeed,
#            "settrdec": SetTrslDec,
#            "setrotacc": SetRotAcc,
#            "setrotmax": SetRotMaxSpeed,
#            "setrotdec": SetRotDec,
            "setx": self.set_x,
            "sety": self.set_y,
            "sett": self.set_theta,
#            "setwheels": SetWheels,
#            "setspacing": SetWheelSpacing,
#            "sw": SetWheels,

            # Get

#            "getpidt": GetPIDTrsl,
#            "getpidr": GetPIDRot,
            "getpos": self.get_position,
            "gp": self.get_position,
#            "getspeeds": GetSpeeds,
#            "getwheels": GetWheels,

#            "tq": TestQueued,
#            "tr": TestRot,
#            "tt": TestTrsl,

            "wasd": self.wasd,
#            "w": w,
#            "a": a,
#            "d": d,
#            "s": s,
        }

        self.recalibration_block = self.wrap_block(self.recalibration)
        self.goto_xy_block = self.wrap_block(self.goto_xy)
        self.goto_theta_block = self.wrap_block(self.goto_theta)

    def wrap_block(self, f):
        def _f(*args, **kwargs):
            self.is_stopped.clear()
            f(*args, **kwargs)
            self.is_stopped.wait()

        return _f

    @Service.event
    def robot_stopped(self):
        self.is_stopped.set()

    def print(self, data):
        if self.do_print:
            if HAVE_PYGMENTS:
                print(highlight(json.dumps(data, sort_keys=True, indent=4),
                        JsonLexer(), Terminal256Formatter()), end='')
            else:
                print(data)

    #########
    # Setup #
    #########

    def recalibration(self, sens):
        try:
            self.print(self.tm.recalibration(sens=sens))
        except: # Recalibration will timeout
            pass

    def flush_serial(self):
        self.print(self.tm.flush_serial())

    def flush_queue(self):
        self.print(self.tm.flush_queue())

    def help(self):
        print(__doc__)

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

    ###########
    # Un/Free #
    ###########

    def free(self):
        self.print(self.tm.free())

    def unfree(self):
        self.print(self.tm.unfree())

    #######
    # Get #
    #######

    def get_position(self):
        self.print(self.tm.get_position())

    #######
    # Set #
    #######

    def set_x(self, x):
        self.print(self.tm.set_x(x=x))

    def set_y(self, y):
        self.print(self.tm.set_y(y=y))

    def set_theta(self, theta):
        self.print(self.tm.set_theta(theta=theta))

    def set_trsl_max_speed(self, maxspeed):
        self.print(self.tm.set_trsl_max_speed(maxspeed=maxspeed))

    ########
    # Jobs #
    ########

    def find_position(self, c):
        """ c = -1 (blue) or c = 1 (red) """
        color = int(c)
        self.free()
        self.set_theta(math.pi / 2.0)
        self.set_trsl_max_speed(200)
        self.set_x(1000)
        self.set_y(1000)
        print("Recalage")
        self.recalibration_block(0)
        print("Stopped")
        print("Y pos found !")
        self.goto_xy_block(1000, 1000)
        self.goto_theta_block(math.pi / 2.0 + math.pi / 2.0 * color)
        self.recalibration_block(0)
        self.goto_xy_block(1500 + 1100 * color, 1000)
        self.set_trsl_max_speed(100)
        self.goto_xy_block(1500 + 1500 * color - 185 / 2.0 * color, 1000)
        self.set_trsl_max_speed(800)
        print("X pos found !")

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

    def wasd(self):
        STEP = 200

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

        curses.echo()
        curses.endwin()
        self.do_print = True

    def loop(self):
        print(__doc__)

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
    shell = Shell()
    thread_loop = Thread(target=shell.loop)
    thread_loop.start()
    shell.run()

if __name__ == "__main__":
    main()

