from cellaserv.proxy import CellaservProxy
from enum import Enum
from math import cos, sin, pi
from os import _exit
from tkinter import *
from PIL import Image
from PIL import ImageTk

class InterfaceStatus(Enum):
    init = 0
    set = 1
    running = 2
    waiting = 3
    end = 4

class MatchInterface:

    def __init__(self, match):

        self.cs = CellaservProxy()

        match_interface_config = self.cs.config.get_section('match')

        self.interface_refresh = int(match_interface_config['interface_refresh'])
        self.interface_ratio = float(match_interface_config['interface_ratio'])
        self.robot_size = float(match_interface_config['robot_size'])
        self.color1 = match_interface_config['color1']
        self.color2 = match_interface_config['color2']

        self.pal_size_y = float(self.cs.config.get(section='pal', option='robot_size_y'))
        self.pmi_size_y = float(self.cs.config.get(section='pmi', option='robot_size_y'))


        self.interface_status = InterfaceStatus.init
        self.match = match

        self.window = Tk()
        self.window.title('Mathc Interface')

        img = Image.open('/etc/conf.d/map.png')
        img = img.resize((int(3000 * self.interface_ratio), int(2000 * self.interface_ratio)), Image.ANTIALIAS)
        self.map = ImageTk.PhotoImage(img)

        print('[MATCH INTERFACE] Window created')

        self.window.after(self.interface_refresh, self.update_interface)
        self.window.mainloop()

    """ PRINT UTILITIES """

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

    """ INTERFACE UTILITIES """

    def close(self):
        self.window.destroy()
        _exit(0)

    def set_color(self, color):
        if self.match.set_color(color):
            self.interface_status = InterfaceStatus.set

    def reset_match(self):
        if self.match.reset_match():
            self.interface_status = InterfaceStatus.init

    # Init color interface
    def set_color_interface(self):
        close_button = Button(self.window, text='Close', command=self.close)
        color1_button = Button(self.window, text=self.color1,
            command=lambda: self.set_color(self.color1), bg=self.color1, height=10, width=20)
        color2_button = Button(self.window, text=self.color2,
            command=lambda: self.set_color(self.color2), bg=self.color2, height=10, width=20)
        close_button.grid(row=1, column=2)
        color1_button.grid(row=3, column=1)
        color2_button.grid(row=3, column=3)

    # Init match interface
    def set_match_interface(self):

        status = self.match.get_match()

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
        if not status['pal_ai_status'] is None:
            text = status['pal_ai_status']
        elif not status['pal_telemetry'] is None:
            text = 'AI not launched'
        self.pal_ai_status_label = Label(self.window, text="PAL status: %s" % text)
        self.pal_ai_status_label.grid(row=2, column=1)

        # PMI AI STATUS
        text = 'PMI not connected'
        if not status['pmi_ai_status'] is None:
            text = status['pmi_ai_status']
        elif not status['pmi_telemetry'] is None:
            text = 'AI not launched'
        self.pmi_ai_status_label = Label(self.window, text="PMI status: %s" % text)
        self.pmi_ai_status_label.grid(row=3, column=1)

        # Color
        self.color_label = Label(self.window, text="Color: %s" % status['color'], fg=status['color'])
        self.color_label.grid(row=2, column=3)

        # Score
        self.score_label = Label(self.window, text="Score: %d" % status['score'])
        self.score_label.grid(row=3, column=3)

        # Match status
        self.match_status_label = Label(self.window, text="Match status: %s" % status['status'])
        self.match_status_label.grid(row=2, column=2)

        # Match time
        self.match_time_label = Label(self.window, text="Match time: %d" % status['time'])
        self.match_time_label.grid(row=3, column=2)

        self.canvas.create_image(1500 * self.interface_ratio, 1000 * self.interface_ratio, image=self.map)

        if status['pal_telemetry'] is not None:
            self.print_robot(status['pal_telemetry'], self.pal_size_y, 'orange')

        if status['pmi_telemetry'] is not None:
            self.print_robot(status['pmi_telemetry'], self.pmi_size_y, 'orange')

        # TODO: use status['robots']
        robots = []
        try:
            robots = self.cs.map.get_opponnents()
        except Exception as e:
            print('[MATCH INTERFACE] Failed to get opponents: %s' % str(e))

        for robot in robots:
            self.print_robot(robot, self.robot_size, 'red')

    # Init score interface
    def set_score_interface(self):

        status = self.match.get_match()

        close_button = Button(self.window, text='Close', command=self.close)
        close_button.grid(row=1, column=1)
        reset_button = Button(self.window, text='Reset Match', command=self.reset_match)
        reset_button.grid(row=1, column=3)
        score_label = Label(self.window, text="Score:\n%d" % status['score'], font=('Mono', 90), fg=status['color'])
        score_label.grid(row=2, column=1, columnspan=3)

    def update_interface(self):

        status = self.match.get_match()

        if self.interface_status != InterfaceStatus.waiting:
            if status['status'] == 'ended':
                self.interface_status = InterfaceStatus.end
            elif status['status'] == 'unstarted':
                if status['color'] == None:
                    self.interface_status = InterfaceStatus.init
                elif self.interface_status != InterfaceStatus.running:
                    self.interface_status = InterfaceStatus.set

        if self.interface_status == InterfaceStatus.running:

            self.canvas.delete('all')
            self.canvas.create_image(1500 * self.interface_ratio, 1000 * self.interface_ratio, image=self.map)

            # PAL AI STATUS
            text = 'PAL not connected'
            if not status['pal_ai_status'] is None:
                text = status['pal_ai_status']
            elif not status['pal_telemetry'] is None:
                text = 'AI not launched'
            self.pal_ai_status_label.config(text="PAL status: %s" % text)

            # PMI AI STATUS
            text = 'PMI not connected'
            if not status['pmi_ai_status'] is None:
                text = status['pmi_ai_status']
            elif not status['pmi_telemetry'] is None:
                text = 'AI not launched'
            self.pmi_ai_status_label.config(text="PMI status: %s" % text)

            self.color_label.config(text="Color: %s" % status['color'])
            self.score_label.config(text="Score: %d" % status['score'])
            self.match_status_label.config(text="Match status: %s" % status['status'])
            self.match_time_label.config(text="Match time: %d" % status['time'])

            if status['pal_telemetry'] is not None:
                self.print_robot(status['pal_telemetry'], self.pal_size_y, 'orange')

            if status['pmi_telemetry'] is not None:
                self.print_robot(status['pmi_telemetry'], self.pmi_size_y, 'orange')

            # TODO: use status['robots']
            robots = []
            try:
                robots = self.cs.map.get_opponnents()
            except Exception as e:
                print('[MATCH INTERFACE] Failed to get opponents: %s' % str(e))

            for robot in robots:
                self.print_robot(robot, self.robot_size, 'red')

            # TODO: Manage path
            #self.print_path(self.pal_path, 'yellow', 'violet')
            #self.print_path(self.pmi_path, 'violet', 'yellow')

        else:
            if self.interface_status != InterfaceStatus.waiting:
                widget_list = self.window.grid_slaves()
                for item in widget_list:
                    item.destroy()

            if self.interface_status == InterfaceStatus.init:
                self.interface_status = InterfaceStatus.waiting
                self.set_color_interface()

            elif self.interface_status == InterfaceStatus.end:
                self.interface_status = InterfaceStatus.waiting
                self.set_score_interface()

            elif self.interface_status == InterfaceStatus.set:
                self.interface_status = InterfaceStatus.running
                self.set_match_interface()

        self.window.after(self.interface_refresh, self.update_interface)
