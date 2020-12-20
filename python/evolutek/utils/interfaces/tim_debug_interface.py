#!/usr/bin/env python3

from evolutek.lib.interface import Interface
from evolutek.lib.map.point import Point
from evolutek.lib.map.tim import Tim, DebugMode
from threading import Thread, Lock 
from evolutek.lib.map.utils import convert_path_to_point
from cellaserv.proxy import CellaservProxy
from tkinter import Button, Canvas, Label
import json

## TODO: Map obstacles
## TODO: Tims
## TODO: Detected opponents

class TimDebugInterface(Interface):

    def __init__(self):

        self.map_enabled = False
        self.tim_enabled = False
        self.tim_debug = True
        self.tim_colors = {"sick1": "red", "sick2": "blue", "sick3": "green"}
        self.tims = {}
        self.scans = {}
        self.clouds = []
        self.lock = Lock()
        self.cs = CellaservProxy()
        super().__init__('Tim Debug', 1)
        self.init_tims()
        self.window.after(self.interface_refresh, self.update_interface)
        print('[TIM DEBUG INTERFACE] Window looping')
        self.window.mainloop()

    def init_tims(self):
        # TIM (lidars) init
        self.tim_debug = False
        self.refresh = int(self.cs.config.get(section='tim', option='refresh'))
        self.tim_computation_config = self.cs.config.get_section('tim')
        self.tims = {}
        self.tim_config = None
        with open('/etc/conf.d/tim.json', 'r') as tim_file:
          self.tim_config = tim_file.read()
          self.tim_config = json.loads(self.tim_config)
        self.robot_size = int(self.cs.config.get(section='match', option='robot_size'))
        self.delta_dist = float(self.cs.config.get(section='tim', option='delta_dist')) * 2
        self.color = None
        self.color1 = self.cs.config.get(section='match', option='color1')
        self.color2 = self.cs.config.get(section='match', option='color2')
        try:
          self.color = self.cs.match.get_color()
        except Exception as e:
          print('[MAP] Failed to get color: %s\nUsing default %s' % (str(e), self.color1))
          self.color = self.color1 # Default color
        for tim in self.tim_config:
          self.tims[tim['ip']] = Tim(tim, self.tim_computation_config, self.color != self.color1)
        self.scan_thread = Thread(target = self.loop_scan)
        self.scan_thread.start()


    def reset_tim(self):
        self.scans = {}
        self.clouds = []

    def change_debug_tim(self):
        self.tim_debug = not self.tim_debug

    def print_polygon(self, points, color):

        for i in range(1, len(points)):
            p1 = Point(dict=points[i - 1])
            p2 = Point(dict=points[i])

            self.canvas.create_line(p1.y * self.interface_ratio, p1.x * self.interface_ratio,
                p2.y * self.interface_ratio, p2.x * self.interface_ratio, width=5, fill=color)

        for p in points:
            point = Point(dict=p)
            x1 = (point.y - 10) * self.interface_ratio
            x2 = (point.y + 10) * self.interface_ratio
            y1 = (point.x - 10) * self.interface_ratio
            y2 = (point.x + 10) * self.interface_ratio
            self.canvas.create_rectangle(x1, y1, x2, y2, fill='violet')

    def print_tims(self, tims):
      for ip in tims:
        tim_points = tims[ip]
        for p in tim_points:
          self.print_point(p, self.tim_colors[ip])

    def print_merge(self, merge):
        for cloud in merge:
          self.print_robot(cloud.merged_pos.to_dict(), 150, "white")
          #for ip in cloud.points:
          #  for point in cloud.points[ip]:
          #    self.print_point(point, self.tim_colors[ip])

    def loop_scan(self):
      while True:
        new_clouds = []
        new_scans = {}
        for ip in self.tims:
          tim = self.tims[ip]
          if not tim.connected:
            pass
          if self.tim_debug:
            new_scans[ip] = tim.get_raw_data()
          else:
            clouds = tim.get_scan()
            for new in clouds:
              merged = False
              for cloud in new_clouds:
                merged = cloud.merge(new, self.delta_dist)
                if merged:
                  break
              if not merged:
                new_clouds.append(new)
        with self.lock:
          self.clouds.clear()
          self.scans.clear()
          self.clouds = new_clouds[:]
          self.scans = new_scans
                

    def init_interface(self):

        # Close button
        close_button = Button(self.window, text='Close', command=self.close)
        close_button.grid(row=1, column=1)

        # TIM debug Button
        self.tim_debug_button = Button(self.window, text='Debug mode: %s' % 'On' if self.tim_debug else 'Off', command=self.change_debug_tim, bg='green' if self.tim_debug else 'red')
        self.tim_debug_button.grid(row=1, column=4)

        # Map
        self.canvas = Canvas(self.window, width=3000 * self.interface_ratio, height= 2000 * self.interface_ratio)
        self.canvas.grid(row=2, column=1, columnspan=4)

        self.canvas.create_image(1500 * self.interface_ratio, 1000 * self.interface_ratio, image=self.map)

    def update_interface(self):

        self.canvas.delete('all')
        self.canvas.create_image((3000 * self.interface_ratio) / 2, (2000 * self.interface_ratio) / 2, image=self.map)

        if self.tim_debug:
          with self.lock:
            self.print_tims(self.scans)
        else:
          with self.lock:
            self.print_merge(self.clouds)

        self.tim_debug_button.config(text='Debug mode: %s' % self.tim_debug, bg='green' if self.tim_debug else 'red')

        self.window.after(self.interface_refresh, self.update_interface)

def main():
    TimDebugInterface()

if __name__ == "__main__":
    main()
