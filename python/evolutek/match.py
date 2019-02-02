from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service
from threading import Timer
from tkinter import *
from time import sleep

#@Service.require('ai', ROBOT)
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
        self.interface_refresh = int(self.cs.config.get(section='match', option='interface_refresh'))
        self.interface_ratio = float(self.cs.config.get(section='match', option='interface_ratio'))
        self.robot_size_x = int(self.cs.config.get(section='pal', option='robot_size_y'))
        self.robot_size_y = int(self.cs.config.get(section='pal', option='robot_size_y'))

        # Match Status
        self.color = None
        self.match_status = 'unstarted'
        self.score = 0
        self.tirette = True
        self.timer = Timer(self.match_time - 5, self.match_end)
        self.match_reseted = True
        self.color_setted = False

        # PAL status
        self.pal_ai_s = None
        self.pal_avoid_s = None
        self.pal_telem = {'x': 1000, 'y':1500}
        self.robots = []

        super().__init__()
        print('Match ready')


    # Publish Match Status
    #@Service.thread
    def update_data(self):
        return
        while True:
            self.publish('match', self.get_match())
            sleep(self.refresh)

    """ Interface """

    def set_color(self, value):
        self.color_setted = True
        self.color = value

    def reset_match(self):
        self.match_reseted = True
        self.color = None

    def set_color_interface(self):
        close_button = Button(self.window, text='Close', command=self.window.destroy)
        green_button = Button(self.window, text=self.color1,
            command=lambda: self.set_color(self.color1), bg=self.color1, height=10, width=20)
        orange_button = Button(self.window, text=self.color2,
            command=lambda: self.set_color(self.color2), bg=self.color2, height=10, width=20)
        close_button.grid(row=1, column=2)
        green_button.grid(row=3, column=1)
        orange_button.grid(row=3, column=3)

    def set_match_interface(self):
        close_button = Button(self.window, text='Close', command=self.window.destroy)
        close_button.grid(row=1, column=2)
        reset_button = Button(self.window, text='Reset Match', command=self.reset_match)
        reset_button.grid(row=2, column=2)
        self.canvas = Canvas(self.window, width=3000 * self.interface_ratio, height= 2000 * self.interface_ratio)
        self.canvas.grid(row=3, column=2)

    def print_robot(self, robot, size, color):
        if robot["shape"] == "circle":
            self.canvas.create_oval(
                (robot['y'] - size/2) * self.interface_ratio,
                (robot['x'] - size/2) * self.interface_ratio,
                (robot['y'] + size/2) * self.interface_ratio,
                (robot['x'] + size/2) * self.interface_ratio,
            width=2, fill=color)
            return
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
        elif self.color is not None:
            if self.color_setted:
                self.color_setted = False
                widget_list = self.window.grid_slaves()
                for item in widget_list:
                    item.destroy()
                self.set_match_interface()
            self.canvas.delete('all')
            self.canvas.create_image(1500 * self.interface_ratio, 1000 * self.interface_ratio, image=self.map)
            if self.pal_telem is not None:
              self.print_robot(self.pal_telem, self.robot_size_y, 'orange')
            for robot in self.robots:
              print(robot)
              self.print_robot(robot, self.robot_size, 'red')

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

    def match_start(self):
        if self.match_started != 'unstarted':
            return
        self.match_status = 'started'
        print('match_start')
        self.cs.ai['PAL'].start()
        self.timer.start()

    # End match
    def match_end(self):
        print('match_end')
        self.ai['PAL'].end()
        self.match_status = 'ended'

    # Update score
    @Service.event
    def score(self, value):
        self.score += int(value)
        print('score is now: %d' % self.score)

    @Service.event
    def pal_telemetry(self, status, telemetry):
        if status != failed:
            self.pal_telem = telemetry
        else:
            print("Could not read telemetry")


    @Service.event
    def oppenents(self, robots):
      self.robots = robots

    # update Tirette
    @Service.event
    def tirette(self, name, id, value):
        print('Tirette: %s' % value)
        tirette = int(value)
        if tirette:
            print('Tirette is inserted')
        elif self.match_status == 'unstarted' and self.tirette:
            self.match_start()
        else:
            print('Tirette was not inserted')
        self.tirette = bool(tirette)

    @Service.event
    def reset(self, value):
        print('reset')
        self.match_status = 'unstarted'
        self.score = 0
        self.timer.cancel()
        self.timer = Timer(self.match_time - 5, self.match_end)
        if value == 'PAL':
            #self.ai.reset(self.color)
            pass

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

        return match

def main():
    match = Match()
    match.run()

if __name__ == '__main__':
    main()
