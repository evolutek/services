#!/usr/bin/env python3

import json
from tkinter import *
from map import wall

radius_pal = 75
radius_mi = 52.5
radius_robot = 75

refresh_interface= 500
unit = 1/2

class Interface:

    def __init__(self, map):

        print('Init interface')

        self.window = Tk()
        self.map = map
        self.width = map.real_width * unit
        self.height = map.real_height * unit
        self.close_button = Button(self.window, text='Close', command=self.window.quit)
        self.close_button.pack()
        self.canvas = Canvas(self.window, width=self.width, height=self.height)
        self.image = PhotoImage(file='map.png')
        self.canvas.create_image(750, 500, image=self.image)

        for x in range(self.map.width + 1):
            for y in range(self.map.height + 1):
                self.canvas.create_oval(x * self.map.unit * unit - 1,
                    y * self.map.unit * unit - 1,
                    x * self.map.unit * unit + 1,
                    y * self.map.unit * unit + 1, fill='red')

        self.print_grid()
        self.print_obstacles()

        #self.print_path(path)

        self.canvas.pack()
        print('Window created')

        #self.window.after(refresh_interface, self.update)
        self.window.mainloop()

    def print_grid(self):
        for x in range(self.map.width):
            x_inf = (x * self.map.unit - self.map.unit/2) * unit
            x_sup = (x * self.map.unit + self.map.unit/2) * unit
            self.canvas.create_line(x_inf, 0, x_inf, self.height, fill='black')
            self.canvas.create_line(x_sup, 0, x_sup, self.height, fill='black')
        for y in range(self.map.height):
            y_inf = (y * self.map.unit - self.map.unit/2) * unit
            y_sup = (y * self.map.unit + self.map.unit/2) * unit
            self.canvas.create_line(0, y_inf, self.width, y_inf, fill='black')
            self.canvas.create_line(0, y_sup, self.width, y_sup, fill='black')

    def print_obstacles(self):
        for y in range(self.map.width + 1):
            for x in range(self.map.height + 1):
                if self.map.map[x][y] == wall:
                    x1 = (y * self.map.unit - self.map.unit/2) * unit
                    x2 = (y * self.map.unit + self.map.unit/2) * unit
                    y1 = (x * self.map.unit - self.map.unit/2) * unit
                    y2 = (x * self.map.unit + self.map.unit/2) * unit
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill='black')

    def print_pal(self, pal):
        if not pal:
            return
        self.canvas.create_rectangle((pal['y']/2) - radius_pal, (pal['x']/2) - radius_pal,
            (pal['y']/2) + radius_pal, (pal['x']/2) + radius_pal, width=2, fill='orange')

    def print_path(self, path):
        begin = path.begin
        self.canvas.create_rectangle((begin.y - self.map.unit/2) / unit,
                (begin.x - self.map.unit/2) / unit, (begin.y + self.map.unit/2) / unit,
                (begin.x + self.map.unit/2) / unit, fill='yellow')
        for p in path.path:
            print(p)
            self.canvas.create_rectangle((p.y - self.map.unit/2) / unit,
                    (p.x - self.map.unit/2) / unit, (p.y + self.map.unit/2) / unit,
                    (p.x + self.map.unit/2) / unit, fill='yellow')

    def update(self):
        self.canvas.delete('all')
        self.canvas.create_image(self.width/2, self.height/2, image=self.image)


        # Display robots

        self.window.after(refresh_interface, self.update)


