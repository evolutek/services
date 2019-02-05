from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service
from evolutek.lib.watchdog import Watchdog
from os import _exit
from threading import Timer
from tkinter import *
from time import sleep

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
        self.tirette = False
        self.timer = Timer(self.match_time - 5, self.match_end)
        self.match_reseted = True
        self.color_setted = False
        self.match_ended = False

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

        super().__init__()
        print('Match ready')


    """ Interface """

    def set_color(self, value):
        self.color_setted = True
        self.color = value
        self.reset()
        try:
            self.cs.ai['pal'].setup(color=self.color, recalibration=False)
            self.cs.ai['pmi'].setup(color=self.color, recalibration=False)
        except Exception as e:
            print('Failed to reset robots: %s' % str(e))

    def reset_match(self):
        if self.match_status == 'started':
            return
        self.match_reseted = True
        self.match_ended = False
        self.color = None

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
        self.match_ended = True
        close_button = Button(self.window, text='Close', command=self.close)
        close_button.grid(row=1, column=1)
        reset_button = Button(self.window, text='Reset Match', command=self.reset_match)
        reset_button.grid(row=1, column=3)
        score_label = Label(self.window, text="Score: %d" % self.score, font=('Mono', 144), fg=self.color)
        score_label.grid(row=2, column=1, columnspan=3)

    def print_robot(self, robot, size, color):
        self.canvas.create_rectangle(
            (robot['y'] - size/2) * self.interface_ratio,
            (robot['x'] - size/2) * self.interface_ratio,
            (robot['y'] + size/2) * self.interface_ratio,
            (robot['x'] + size/2) * self.interface_ratio,
            width=2, fill=color)

    def update_interface(self):
        if self.match_reseted and self.color is None:
            self.match_reseted = False
            widget_list = self.window.grid_slaves()
            for item in widget_list:
                item.destroy()
            self.set_color_interface()
        elif self.match_status == 'ended' and not self.match_ended and self.color is not None:
            widget_list = self.window.grid_slaves()
            for item in widget_list:
                item.destroy()
            self.set_score_interface()
        elif self.color is not None and not self.match_ended:
            if self.color_setted:
                self.color_setted = False
                widget_list = self.window.grid_slaves()
                for item in widget_list:
                    item.destroy()
                self.set_match_interface()
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

    @Service.thread
    def launch_interface(self):
        if not self.interface_enabled:
          return
        self.window = Tk()
        self.window.title('Match interface')

        self.map = PhotoImage(file='map.png')

        print('Window created')
        self.window.after(self.interface_refresh, self.update_interface)
        self.window.mainloop()


    """ Match utilities """

    def match_start(self):
        if self.match_status != 'unstarted':
            return

        try:
            self.cs.ai['pal'].start()
            self.cs.ai['pmi'].start()
        except Exception as e:
            print('Failed to start match: %s' % str(e))

        self.timer.start()
        self.match_status = 'started'
        print('match_start')

    # End match
    def match_end(self):
        try:
            self.cs.ai['pal'].end()
            self.cs.ai['pmi'].end()
        except Exception as e:
            print('Failed to stop robots: %s', str(e))
        self.match_status = 'ended'
        print('match_end')

    def reset_pal_status(self):
        self.pal_ai_s = None
        self.pal_telem = None
        self.pal_avoid_s = None

    def reset_pmi_status(self):
        self.pmi_ai_s = None
        self.pmi_telem = None
        self.pmi_avoid_s = None


    """ Event """

    # Update score
    @Service.event
    def score(self, value):
        if self.match_status != 'started':
            return
        self.score += int(value)
        print('score is now: %d' % self.score)

    @Service.event
    def pal_telemetry(self, status, telemetry):
        self.pal_watchdog.reset()
        if status != failed:
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

    @Service.event
    def pmi_telemetry(self, status, telemetry):
        self.pmi_watchdog.reset()
        if status != failed:
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

    @Service.event
    def oppenents(self, robots):
      self.robots = robots

    # update Tirette
    @Service.event
    def tirette(self, value, _=None):
        print('Tirette: %s' % value)
        tirette = int(value)
        if tirette:
            print('Tirette is inserted')
        elif self.match_status == 'unstarted' and self.tirette:
            self.match_start()
        else:
            print('Tirette is not inserted')
        self.tirette = bool(tirette)

    @Service.event
    def reset(self, _=None):
        if self.match_status == 'started':
            return
        print('reset')
        self.match_status = 'unstarted'
        self.score = 0
        self.timer = Timer(self.match_time - 5, self.match_end)


    """ Action """

    @Service.action
    def get_color(self):
        return self.color

    @Service.action
    def get_match(self):
        match = {}

        match['status'] = self.match_status
        match['color'] = self.color
        match['robots'] = self.robots
        match['score'] = self.score
        match['tirette'] = self.tirette

        match['pal_ai_status'] = self.pal_ai_s
        match['pal_avoid_status'] = self.pal_avoid_s
        match['pal_telemetry'] = self.pal_telem

        match['pmi_ai_status'] = self.pmi_ai_s
        match['pmi_avoid_status'] = self.pmi_avoid_s
        match['pmi_telemetry'] = self.pmi_telem

        return match


def main():
    match = Match()
    match.run()

if __name__ == '__main__':
    main()
