import socket
from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service
from evolutek.lib.watchdog import Watchdog
from evolutek.lib.waiter import waitBeacon, waitConfig
from math import cos, sin, pi
from os import _exit
from threading import Timer, Thread
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
        waitConfig(self.cs)
        # Match Params
        match_config = self.cs.config.get_section('match')
        self.color1 = match_config['color1']
        self.color2= match_config['color2']
        self.match_time = int(match_config['time'])
        self.refresh = float(match_config['refresh'])
        self.robot_size = float(match_config['robot_size'])
        self.interface_enabled = match_config['interface_enabled']
        self.timeout_robot = float(match_config['timeout_robot'])
        self.interface_refresh = int(match_config['interface_refresh'])
        self.interface_ratio = float(match_config['interface_ratio'])

        # Robots config
        self.pal_size_x = float(self.cs.config.get(section='pal', option='robot_size_x'))
        self.pal_size_y = float(self.cs.config.get(section='pal', option='robot_size_y'))
        self.pmi_size_x = float(self.cs.config.get(section='pmi', option='robot_size_x'))
        self.pmi_size_y = float(self.cs.config.get(section='pmi', option='robot_size_y'))

        # Match Status
        self.color = None
        self.match_status = 'unstarted'
        self.score = 0
        self.timer = Timer(self.match_time, self.match_end)
        self.match_time = 0
        self.match_time_thread = Thread(target=self.match_time_loop)
        self.interface_status = InterfaceStatus.init

        # PAL status
        self.pal_ai_s = None
        self.pal_telem = None
        self.pal_path = []
        self.pal_watchdog = Watchdog(self.timeout_robot * 1.5, self.reset_pal_status)

        # PMI status
        self.pmi_ai_s = None
        self.pmi_telem = None
        self.pmi_path = []
        self.pmi_watchdog = Watchdog(self.timeout_robot * 1.5, self.reset_pmi_status)

        # Oppenents positions
        self.robots = []
        self.robots_watchdog = Watchdog(self.timeout_robot * 3, self.reset_robots)

        super().__init__()
        print('[MATCH] Match ready')


    """ INTERFACE """

    def close(self):
        self.window.destroy()
        _exit(0)

    def set_color_interface(self):
        close_button = Button(self.window, text='Close', command=self.close)
        color1_button = Button(self.window, text=self.color1,
            command=lambda: self.set_color(self.color1), bg=self.color1, height=10, width=20)
        color2_button = Button(self.window, text=self.color2,
            command=lambda: self.set_color(self.color2), bg=self.color2, height=10, width=20)
        close_button.grid(row=1, column=2)
        color1_button.grid(row=3, column=1)
        color2_button.grid(row=3, column=3)

    def set_match_interface(self):

        # Close button
        close_button = Button(self.window, text='Close', command=self.close)
        close_button.grid(row=1, column=1)

        # Reset Button
        reset_button = Button(self.window, text='Reset Match', command=self.reset_match)
        reset_button.grid(row=1, column=3)

        # Map
        self.canvas = Canvas(self.window, width=3000 * self.interface_ratio, height= 2000 * self.interface_ratio)
        self.canvas.grid(row=4, column=1, columnspan=3)

        # PAL AI STATUS
        text = 'PAL not connected'
        if not self.pal_ai_s is None:
            text = self.pal_ai_s
        elif not self.pal_telem is None:
            text = 'AI not launched'
        self.pal_ai_status_label = Label(self.window, text="PAL status: %s" % text)
        self.pal_ai_status_label.grid(row=2, column=1)

        # PMI AI STATUS
        text = 'PMI not connected'
        if not self.pmi_ai_s is None:
            text = self.pmi_ai_s
        elif not self.pmi_telem is None:
            text = 'AI not launched'
        self.pmi_ai_status_label = Label(self.window, text="PMI status: %s" % text)
        self.pmi_ai_status_label.grid(row=3, column=1)

        # Color
        self.color_label = Label(self.window, text="Color: %s" % self.color, fg=self.color)
        self.color_label.grid(row=2, column=3)

        # Score
        self.score_label = Label(self.window, text="Score: %d" % self.score)
        self.score_label.grid(row=3, column=3)

        # Match status
        self.match_status_label = Label(self.window, text="Match status: %s" % self.match_status)
        self.match_status_label.grid(row=2, column=2)

        # Match time
        self.match_time_label = Label(self.window, text="Match time: %d" % self.match_time)
        self.match_time_label.grid(row=3, column=2)

    def set_score_interface(self):
        close_button = Button(self.window, text='Close', command=self.close)
        close_button.grid(row=1, column=1)
        reset_button = Button(self.window, text='Reset Match', command=self.reset_match)
        reset_button.grid(row=1, column=3)
        score_label = Label(self.window, text="Score:\n%d" % self.score, font=('Mono', 90), fg=self.color)
        score_label.grid(row=2, column=1, columnspan=3)

    def print_robot(self, robot, size, color):
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

    def print_path(self, path, color_path, color_point):
        size = 10 * self.interface_ratio
        for i in range(1, len(path)):
            p1 = path[i - 1]
            p2 = path[i]

            self.canvas.create_line(p1['y'] * self.interface_ratio, p1['x'] * self.interface_ratio,
                p2['y'] * self.interface_ratio, p2['x'] * self.interface_ratio, width=size, fill=color_path)

        for p in path:
            x1 = (p['y'] - size) * self.interface_ratio
            x2 = (p['y'] + size) * self.interface_ratio
            y1 = (p['x'] - size) * self.interface_ratio
            y2 = (p['x'] + size) * self.interface_ratio
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=color_point)


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

            try:
                self.robots = self.cs.map.get_opponnents()
            except:
                pass

            for robot in self.robots:
                self.print_robot(robot, self.robot_size, 'red')

            self.print_path(self.pal_path, 'yellow', 'violet')
            self.print_path(self.pmi_path, 'violet', 'yellow')

            # PAL AI STATUS
            text = 'PAL not connected'
            if not self.pal_ai_s is None:
                text = self.pal_ai_s
            elif not self.pal_telem is None:
                text = 'AI not launched'
            self.pal_ai_status_label.config(text="PAL status: %s" % text)

            # PMI AI STATUS
            text = 'PMI not connected'
            if not self.pmi_ai_s is None:
                text = self.pmi_ai_s
            elif not self.pmi_telem is None:
                text = 'AI not launched'
            self.pmi_ai_status_label.config(text="PMI status: %s" % text)

            self.color_label.config(text="Color: %s" % self.color)
            self.score_label.config(text="Score: %d" % self.score)
            self.match_status_label.config(text="Match status: %s" % self.match_status)
            self.match_time_label.config(text="Match time: %d" % self.match_time)

        self.window.after(self.interface_refresh, self.update_interface)


    """ MATCH UTILITIES """

    def reset_pal_status(self):
        self.pal_ai_s = None
        self.pal_telem = None
        self.pmi_path = []

    def reset_pmi_status(self):
        self.pmi_ai_s = None
        self.pmi_telem = None
        self.pmi_path = []

    def reset_robots(self):
        self.robots = []

    # Ports : 4343=yellow; 4141=pink
    def start_experiment(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("192.168.8.10", 4343 if self.color == self.color1 else 4141))
        s.close()

    # TODO: LCD on exp function

    """ EVENT """

    """ Update score """
    @Service.event('score')
    def get_score(self, value=0):
        if self.match_status != 'started':
            return
        self.score += int(value)
        print('[MATCH] score is now: %d' % self.score)

    """ PAL """
    @Service.event
    def pal_telemetry(self, status, telemetry):
        self.pal_watchdog.reset()
        if status != 'failed':
            self.pal_telem = telemetry
        else:
            self.pal_telem = None

    @Service.event
    def pal_ai_status(self, status, path):
        self.pal_watchdog.reset()
        self.pal_ai_s = status
        self.pal_path = path

    """ PMI """
    @Service.event
    def pmi_telemetry(self, status, telemetry):
        self.pmi_watchdog.reset()
        if status != 'failed':
            self.pmi_telem = telemetry
        else:
            self.pmi_telem = None

    @Service.event
    def pmi_ai_status(self, status):
        self.pmi_watchdog.reset()
        self.pmi_ai_s = status

    """ Oppenents """
    @Service.event
    def opponents(self, robots):
      self.robots = robots
      self.robots_watchdog.reset()

    """ Tirette """
    @Service.event('tirette')
    def match_start(self, name, id, value):
        if self.match_status != 'unstarted' or self.color is None:
            return

        self.publish('match_start')
        self.timer.start()
        self.match_status = 'started'
        print('[MATCH] Match start')
        self.match_time_thread.start()

        try:
            self.start_experiment()
            self.score += 40
        except:
            pass


    """ ACTION """

    """ Reset match """
    @Service.action
    def reset_match(self, color=None):
        if self.match_status == 'started':
            return False

        print('Reset match')
        self.match_status = 'unstarted'
        self.score = 0
        self.timer = Timer(self.match_time, self.match_end)
        self.match_time = 0
        self.match_time_thread = Thread(target=self.match_time_loop)

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
            print('[MATCH] Invalid color')
            return False

        self.color = color
        self.interface_status = InterfaceStatus.set

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
        match['pal_telemetry'] = self.pal_telem

        match['pmi_ai_status'] = self.pmi_ai_s
        match['pmi_telemetry'] = self.pmi_telem

        return match

    """ End match """
    @Service.action
    def match_end(self):
        self.publish('match_end')
        self.match_status = 'ended'
        self.interface_status = InterfaceStatus.end
        print('[MATCH] Match End')


    """ THREAD """

    """ Match status thread """
    #@Service.thread
    def match_status(self):
      while True:
        #Usefull ?
        #self.publish('match_status', match=self.get_match())

        # Update PAL LCD
        # TODO: Use LCD on exp
        try:
            pass
        except:
            pass
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

        print('[MATCH] Window created')
        self.window.after(self.interface_refresh, self.update_interface)
        self.window.mainloop()

    def match_time_loop(self):
        while self.match_status == 'started':
            self.match_time += 1
            sleep(1)

def main():
    waitBeacon()
    match = Match()
    match.run()

if __name__ == '__main__':
    main()
