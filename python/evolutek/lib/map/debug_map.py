#!/usr/bin/env python3
from evolutek.lib.map.map import ObstacleType
from evolutek.lib.map.point import Point
from evolutek.lib.map.tim import DebugMode

from tkinter import *
from PIL import Image
from PIL import ImageTk
from math import ceil
from os import _exit
from shapely.geometry import Polygon, LineString

colors = ["yellow", "orange", "red", "purple", "blue", "cyan", "green"]
unit = 1/2
refresh = 50


#TODO: add robot angle
class Interface:

    def __init__(self, map, service):

        print('[DEBUG_MAP] Init interface')

        self.window = Tk()
        self.unit = self.window
        self.window.attributes('-fullscreen', True)
        self.window.bind('<Escape>',lambda e: self.close())
        self.window.title('Map interface')

        self.map = map
        self.service = service

        unit_width = self.window.winfo_screenwidth() / self.map.width
        unit_height = self.window.winfo_screenheight() / (self.map.height + 50)
        self.unit = min(unit_width, unit_height)

        self.width = self.map.width * self.unit
        self.height = self.map.height * self.unit

        nb_tims = len(self.service.tim)
        center = int(ceil(nb_tims/2))

        self.close_button = Button(self.window, text='Close', command=self.close)
        self.close_button.grid(row=1, column=center)

        self.tim_labels = []
        i = 1
        for ip in self.service.tim:
            connected = self.service.tim[ip].connected
            label = Label(self.window,
                text='TIM %s: %s' % (ip, 'connected' if connected  else 'disconnected'),
                fg='green' if connected else 'red', height=1)
            label.grid(row=2, column=i)
            i += 1
            self.tim_labels.append((label, ip))

        self.canvas = Canvas(self.window, width=self.width, height=self.height)

        img = Image.open('/etc/conf.d/map.png')
        img = img.resize((int(self.width), int(self.height)), Image.ANTIALIAS)
        self.image =  ImageTk.PhotoImage(img)

        self.canvas.create_image(int(self.width / 2), int(self.height / 2), image=self.image)
        self.canvas.grid(row=3, column=1, columnspan=nb_tims)

        print('[DEBUG_MAP] Window created')
        self.window.after(refresh, self.update)
        self.window.mainloop()

    def close(self):
        self.window.destroy()
        _exit(0)

    def update_tims(self):

        for label, ip in self.tim_labels:
            connected = self.service.tim[ip].connected
            label.config(text='TIM %s: %s' % (ip, 'connected' if connected  else 'disconnected'),
            fg='green' if connected else 'red')

    def print_raw_data(self, raw_data):
        for p in raw_data:
            self.canvas.create_rectangle(p.y * self.unit, p.x * self.unit, p.y * self.unit + 5, p.x * self.unit + 5, fill='white')

    def print_shapes(self, shapes, color):
        for i in range(len(shapes)):
            for p in shapes[i]:
                self.canvas.create_rectangle(p.y * self.unit, p.x * self.unit, p.y * self.unit + 5, p.x * self.unit + 5, fill=color)

    def print_robots(self, robots, color):
        for i in range(len(robots)):
            if not isinstance(robots[i], Point):
                p = Point(dict=robots[i])
            else:
                p = robots[i]
            self.canvas.create_rectangle(p.y * self.unit, p.x * self.unit, p.y * self.unit + 10, p.x * self.unit + 10, fill=color)

    def print_tims(self, debug_tims=False):
        i = 0
        for ip in self.service.tim:
            tim = self.service.tim[ip]
            color = colors[i % len(colors)]
            self.print_raw_data(tim.raw_data)
            if debug_tims:
                self.print_shapes(tim.shapes, color)
                self.print_robots(tim.robots, color)
            i += 1

    def print_polygon(self, points, color):

        for i in range(1, len(points)):
            p1 = Point(tuple=points[i - 1])
            p2 = Point(tuple=points[i])

            self.canvas.create_line(p1.y * self.unit, p1.x * self.unit,
                p2.y * self.unit, p2.x * self.unit, width=5, fill=color)

        for p in points:
            point = Point(tuple=p)
            x1 = (point.y - 10) * self.unit
            x2 = (point.y + 10) * self.unit
            y1 = (point.x - 10) * self.unit
            y2 = (point.x + 10) * self.unit
            self.canvas.create_rectangle(x1, y1, x2, y2, fill='violet')

    def print_map(self):
        self.print_polygon(self.map.borders.exterior.coords)
        for interior in self.map.borders.interiors:
            self.print_polygon(interior.coords)
        for poly in self.map.color_obstacles:
            print(self.map.color_obstacles[poly])
            self.print_polygon(self.map.color_obstacles[poly].exterior.coords, ObstacleType.color)
        for poly in self.map.robots:
            self.print_polygon(self.map.robots[poly].exterior.coords, ObstacleType.robot)

    def print_merged_map(self):

        #merged_map = self.map.merge_map()
        merged_map = self.map.merged_map
        if isinstance(merged_map, Polygon):
            merged_map = [merged_map]

        #self.print_polygon(self.map.borders.exterior.coords, 'black')

        for poly in merged_map:
            self.print_polygon(poly.exterior.coords, 'grey')
            for interior in poly.interiors:
                self.print_polygon(interior.coords, 'red')

    def print_path(self, path):

        for i in range(1, len(path)):
            p1 = path[i - 1]
            p2 = path[i]

            self.canvas.create_line(p1.y * self.unit, p1.x * self.unit,
                p2.y * self.unit, p2.x * self.unit, width=5, fill='yellow')

        for p in path:
            x1 = (p.y - 10) * self.unit
            x2 = (p.y + 10) * self.unit
            y1 = (p.x - 10) * self.unit
            y2 = (p.x + 10) * self.unit
            self.canvas.create_rectangle(x1, y1, x2, y2, fill='violet')

    def print_graph(self, graph):

        for point in graph:

            for p in graph[point]:

                self.canvas.create_line(point.y * self.unit, point.x * self.unit,
                    p.y * self.unit, p.x * self.unit, width=5, fill='yellow')

        for p in graph:
            x1 = (p.y - 10) * self.unit
            x2 = (p.y + 10) * self.unit
            y1 = (p.x - 10) * self.unit
            y2 = (p.x + 10) * self.unit
            self.canvas.create_rectangle(x1, y1, x2, y2, fill='violet')

    def update(self):

        #print('[DEBUG_MAP] Update interface')
        self.canvas.delete('all')
        self.canvas.create_image(int(self.width / 2), int(self.height / 2), image=self.image)
        #self.print_map()
        with self.service.lock:
            self.print_merged_map()

        self.update_tims()

        # Debug Mode
        if self.service.debug_mode != DebugMode.normal:
            self.print_tims(self.service.debug_mode==DebugMode.debug_tims)
            if self.service.debug_mode == DebugMode.debug_merge:
                with self.service.lock:
                    self.print_robots(self.service.robots, 'white')

        """if hasattr(self.service, 'pal_telem') and hasattr(self.service, 'pal_size_y'):
            self.print_robot(self.service.pal_telem, self.service.pal_size_y)
        if hasattr(self.service, 'pmi_telem') and hasattr(self.service, 'pmi_size_y'):
            self.print_robot(self.service.pmi_telem, self.service.pmi_size)"""

        if hasattr(self.service, 'path'):
            self.print_path(self.service.path)
        self.window.after(refresh, self.update)
