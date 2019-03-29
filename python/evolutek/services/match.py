from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service
from evolutek.lib.watchdog import Watchdog
from math import cos, sin, pi
from os import _exit
from threading import Timer
from tkinter import *
from PIL import Image
from PIL import ImageTk
from time import sleep
from enum import Enum

class InterfaceStatus(Enum):
    init = 0
    set = 1
    running = 2
    waiting = 3
    end = 4

@Service.require('config')
class Match(Service):

    def __init__(self):

        self.cs = CellaservProxy()

        # Match Params
        self.color1 = self.cs.config.get(section='match', option='color1')
        self.color2 = self.cs.config.get(section='match', option='color2')
        self.match_time = int(self.cs.config.get(section='match', option='time'))
        self.refresh = float(self.cs.config.get(section='match', option='refresh'))
        self.robot_size = int(self.cs.config.get(section='match', option='robot_size'))
        self.interface_enabled = self.cs.config.get(section='match', option='interface_enabled') == 'True'
        self.timeout_robot = float(self.cs.config.get(section='match', option='timeout_robot'))
        self.interface_refresh = int(self.cs.config.get(section='match', option='interface_refresh'))
        self.interface_ratio = float(self.cs.config.get(section='match', option='interface_ratio'))
        self.pal_size_x = int(self.cs.config.get(section='pal', option='robot_size_x'))
        self.pal_size_y = int(self.cs.config.get(section='pal', option='robot_size_y'))
        self.pmi_size_x = int(self.cs.config.get(section='pmi', option='robot_size_x'))
        self.pmi_size_y = int(self.cs.config.get(section='pmi', option='robot_size_y'))

        # Match Status
        self.color = None
        self.match_status = 'unstarted'
        self.score = 0
        self.timer = Timer(self.match_time - 5, self.match_end)
        self.interface_status = InterfaceStatus.init

        # PAL status
        self.pal_ai_s = None
        self.pal_avoid_s = None
        self.pal_telem = None
        self.pal_watchdog = Watchdog(self.timeout_robot, self.reset_pal_status)

        # PMI status
        self.pmi_ai_s = None
        self.pmi_avoid_s = None
        self.pmi_telem = None
        self.pmi_watchdog = Watchdog(self.timeout_robot, self.reset_pmi_status)

        # Oppenents positions
        self.robots = []
        self.robots_watchdog = Watchdog(self.timeout_robot, self.reset_robots)

        super().__init__()
        print('Match ready')


    """ Interface """

    def close(self):
        self.window.destroy()
        _exit(0)

    def set_color_interface(self):
        close_button = Button(self.window, text='Close', command=self.close)
        green_button = Button(self.window, text=self.color1,
            command=lambda: self.set_color(self.color1), bg=self.color1, height=10, width=20)
        orange_button = Button(self.window, text=self.color2,
            command=lambda: self.set_color(self.color2), bg=self.color2, height=10, width=20)
        close_button.grid(row=1, column=2)
        green_button.grid(row=3, column=1)
        orange_button.grid(row=3, column=3)

    def set_match_interface(self):
        close_button = Button(self.window, text='Close', command=self.close)
        close_button.grid(row=1, column=1)
        reset_button = Button(self.window, text='Reset Match', command=self.reset_match)
        reset_button.grid(row=1, column=3)
        self.canvas = Canvas(self.window, width=3000 * self.interface_ratio, height= 2000 * self.interface_ratio)
        self.canvas.grid(row=4, column=1, columnspan=3)
        self.pal_ai_status_label = Label(self.window,
            text="PAL status: %s" % (self.pal_ai_s if self.pal_ai_s is not None else 'PAL not connected'))
        self.pal_ai_status_label.grid(row=2, column=1)
        self.pmi_ai_status_label = Label(self.window,
            text="PMI status: %s" % (self.pmi_ai_s if self.pmi_ai_s is not None else 'PMI not connected'))
        self.pmi_ai_status_label.grid(row=3, column=1)
        self.color_label = Label(self.window, text="Color: %s" % self.color, fg=self.color)
        self.color_label.grid(row=2, column=3)
        self.score_label = Label(self.window, text="Score: %d" % self.score)
        self.score_label.grid(row=3, column=3)
        self.match_status_label = Label(self.window, text="Match status: %s" % self.match_status)
        self.match_status_label.grid(row=2, column=2)

    def set_score_interface(self):
        close_button = Button(self.window, text='Close', command=self.close)
        close_button.grid(row=1, column=1)
        reset_button = Button(self.window, text='Reset Match', command=self.reset_match)
        reset_button.grid(row=1, column=3)
        score_label = Label(self.window, text="Score:\n%d" % self.score, font=('Mono', 90), fg=self.color)
        score_label.grid(row=2, column=1, columnspan=3)

    def print_robot(self, robot, size, color):
        if "shape" in robot and robot["shape"] == "circle":
            self.canvas.create_oval(
                (robot['y'] - size) * self.interface_ratio,
                (robot['x'] - size) * self.interface_ratio,
                (robot['y'] + size) * self.interface_ratio,
                (robot['x'] + size) * self.interface_ratio,
                width=2, fill=color)
            return
        if 'theta' in robot:
            x = robot['y'] * self.interface_ratio
            y = robot['x'] * self.interface_ratio
            size *= self.interface_ratio

            points = []
            points.append((x - size, y - size))
            points.append((x + size, y - size))
            points.append((x + size, y + size))
            points.append((x - size, y + size))

            cos_val = cos(pi/2 - robot['theta'])
            sin_val = sin(pi/2 - robot['theta'])

            new_points = []
            for point in points:
                new_points.append((
                    (point[0] - x) * cos_val - (point[1] - y) * sin_val + x,
                    (point[0] - x) * sin_val + (point[1] - y) * cos_val + y
                ))

            self.canvas.create_polygon(new_points, fill=color)
            return
        self.canvas.create_rectangle(
            (robot['y'] - size) * self.interface_ratio,
            (robot['x'] - size) * self.interface_ratio,
            (robot['y'] + size) * self.interface_ratio,
            (robot['x'] + size) * self.interface_ratio,
            width=2, fill=color)


    def update_interface(self):
        if self.interface_status == InterfaceStatus.init:
            self.interface_status = InterfaceStatus.waiting
            widget_list = self.window.grid_slaves()
            for item in widget_list:
                item.destroy()
            self.set_color_interface()
        elif self.interface_status == InterfaceStatus.end:
            self.interface_status = InterfaceStatus.waiting
            widget_list = self.window.grid_slaves()
            for item in widget_list:
                item.destroy()
            self.set_score_interface()
        elif self.interface_status == InterfaceStatus.set:
            self.interface_status = InterfaceStatus.running
            widget_list = self.window.grid_slaves()
            for item in widget_list:
                item.destroy()
            self.set_match_interface()

        if self.interface_status == InterfaceStatus.running:
            self.canvas.delete('all')
            self.canvas.create_image(1500 * self.interface_ratio, 1000 * self.interface_ratio, image=self.map)

            if self.pal_telem is not None:
                self.print_robot(self.pal_telem, self.pal_size_y, 'orange')

            if self.pmi_telem is not None:
                self.print_robot(self.pmi_telem, self.pmi_size_y, 'orange')

            for robot in self.robots:
              print(robot)
              self.print_robot(robot, self.robot_size, 'red')

            self.pal_ai_status_label.config(text="PAL status: %s" % (self.pal_ai_s if self.pal_ai_s is not None else 'PAL not connected'))
            self.pmi_ai_status_label.config(text="PMI status: %s" % (self.pmi_ai_s if self.pmi_ai_s is not None else 'PMI not connected'))

            self.color_label.config(text="Color: %s" % self.color)
            self.score_label.config(text="Score: %d" % self.score)
            self.match_status_label.config(text="Match status: %s" % self.match_status)

        self.window.after(self.interface_refresh, self.update_interface)


    """ Match utilities """

    def match_start(self):
        if self.match_status != 'unstarted' and self.color is None:
            return

        try:
            self.cs.ai['pal'].start()
            self.cs.ai['pmi'].start()
        except Exception as e:
            print('Failed to start match: %s' % str(e))

        self.timer.start()
        self.match_status = 'started'
        print('match_start')

    def reset_pal_status(self):
        self.pal_ai_s = None
        self.pal_telem = None
        self.pal_avoid_s = None

    def reset_pmi_status(self):
        self.pmi_ai_s = None
        self.pmi_telem = None
        self.pmi_avoid_s = None

    def reset_robots(self):
        self.robots = []

    """ Event """

    """ Update score """
    @Service.event('score')
    def get_score(self, value):
        if self.match_status != 'started':
            return
        self.score += int(value)
        print('score is now: %d' % self.score)


    """ PAL """
    @Service.event
    def pal_telemetry(self, status, telemetry):
        self.pal_watchdog.reset()
        if status != 'failed':
            self.pal_telem = telemetry
        else:
            self.pal_telem = None
            print("Could not read telemetry")

    @Service.event
    def pal_ai_status(self, status):
        self.pal_watchdog.reset()
        self.pal_ai_s = status

    @Service.event
    def pal_avoid_status(self, status):
        self.pal_watchdog.reset()
        self.pal_avoid_s = status


    """ PMI """
    @Service.event
    def pmi_telemetry(self, status, telemetry):
        self.pmi_watchdog.reset()
        if status != 'failed':
            self.pmi_telem = telemetry
        else:
            self.pmi_telem = None
            print("Could not read telemetry")

    @Service.event
    def pmi_ai_status(self, status):
        self.pmi_watchdog.reset()
        self.pmi_ai_s = status

    @Service.event
    def pmi_avoid_status(self, status):
        self.pmi_watchdog.reset()
        self.pmi_avoid_s = status


    """ oppenents """
    @Service.event
    def oppenents(self, robots):
      self.robots = robots
      self.robots_watchdog.reset()

    """ Tirette """
    @Service.event('tirette')
    def match_start(self):
        if self.match_status != 'unstarted' and self.color is None:
            return

        try:
            self.cs.ai['pal'].start()
            self.cs.ai['pmi'].start()
        except Exception as e:
            print('Failed to start match: %s' % str(e))

        self.timer.start()
        self.match_status = 'started'
        print('match_start')


    """ Action """

    """ Reset match """
    @Service.action
    def reset_match(self, color=None):
        if self.match_status == 'started':
            return False

        print('reset')
        self.match_status = 'unstarted'
        self.score = 0
        self.timer = Timer(self.match_time - 5, self.match_end)

        if not self.set_color(color):
            self.interface_status = InterfaceStatus.init

        return True

    """ Get color """
    @Service.action
    def get_color(self):
        return self.color

    """ Set color """
    @Service.action
    def set_color(self, color):
        if color != self.color1 and color != self.color2:
            print('Invalid color')
            return False

        self.color = color
        self.interface_status = InterfaceStatus.set

        try:
            self.cs.ai['pal'].setup(color=self.color, recalibration=False)
            self.cs.ai['pmi'].setup(color=self.color, recalibration=False)
        except Exception as e:
            print('Failed to reset robots: %s' % str(e))

        self.publish('match_color', color=self.color)

        return True

    """ Get match """
    @Service.action
    def get_match(self):
        match = {}

        match['status'] = self.match_status
        match['color'] = self.color
        match['robots'] = self.robots
        match['score'] = self.score

        match['pal_ai_status'] = self.pal_ai_s
        match['pal_avoid_status'] = self.pal_avoid_s
        match['pal_telemetry'] = self.pal_telem

        match['pmi_ai_status'] = self.pmi_ai_s
        match['pmi_avoid_status'] = self.pmi_avoid_s
        match['pmi_t:elemetry'] = self.pmi_telem

        return match

    """ End match """
    @Service.action
    def match_end(self):
        try:
            self.cs.ai['pal'].end()
            self.cs.ai['pmi'].end()
        except Exception as e:
            print('Failed to stop robots: %s' % str(e))
        self.match_status = 'ended'
        self.interface_status = InterfaceStatus.end
        print('match_end')

    """ Match status thread """
    #@Service.thread
    def match_status(self):
      while True:
        self.publish('match_status', match=self.get_match())
        sleep(self.refresh)

    """ Interface thread """
    @Service.thread
    def launch_interface(self):
        if not self.interface_enabled:
          return
        self.window = Tk()
        self.window.title('Match interface')

        img = Image.open('/etc/conf.d/map.png')
        img = img.resize((int(3000 * self.interface_ratio), int(2000 * self.interface_ratio)), Image.ANTIALIAS)
        self.map =  ImageTk.PhotoImage(img)

        print('Window created')
        self.window.after(self.interface_refresh, self.update_interface)
        self.window.mainloop()

def main():
    match = Match()
    match.run()

if __name__ == '__main__':
    main()
