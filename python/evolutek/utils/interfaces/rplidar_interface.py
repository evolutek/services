from evolutek.lib.interface import Interface
from evolutek.lib.map.point import Point
from threading import Thread, Lock
from evolutek.lib.map.utils import convert_path_to_point
from tkinter import Button, Canvas, Label
import json

class RplidarInterface(Interface):

    def __init__(self, lidar):
        super().__init__('RpLidar', 1)
        self.lidar = lidar
        self.interface_refresh = 100
        self.window.after(self.interface_refresh, self.update_interface)
        print('[RPLIDAR INTERFACE] Window looping')
        self.window.mainloop()


    def print_polygon(self, points, color):

        for i in range(1, len(points)):
            p1 = points[i-1]
            p2 = points[i]
            self.canvas.create_line(p1.y * self.interface_ratio, p1.x * self.interface_ratio,
                p2.y * self.interface_ratio, p2.x * self.interface_ratio, width=5, fill=color)

        for point in points:
            x1 = (point.y - 10) * self.interface_ratio
            x2 = (point.y + 10) * self.interface_ratio
            y1 = (point.x - 10) * self.interface_ratio
            y2 = (point.x + 10) * self.interface_ratio
            self.canvas.create_rectangle(x1, y1, x2, y2, fill='violet')


    def init_interface(self):

        # Close button
        close_button = Button(self.window, text='Close', command=self.close)
        close_button.grid(row=1, column=1)

        # Map
        self.canvas = Canvas(self.window, width=3000 * self.interface_ratio, height= 2000 * self.interface_ratio)
        self.canvas.grid(row=2, column=1, columnspan=4)

        self.canvas.create_image(1500 * self.interface_ratio, 1000 * self.interface_ratio, image=self.map)


    def update_interface(self):

        self.canvas.delete('all')
        self.canvas.create_image((3000 * self.interface_ratio) / 2, (2000 * self.interface_ratio) / 2, image=self.map)

        for point in self.lidar.get_cloud():
            self.print_point(point, 'magenta')

        colors = ['red', 'green', 'blue', 'pink', 'orange', 'violet']
        colori = 0
        for shape in self.lidar.get_shape():
            self.print_polygon(shape, colors[colori])
            colori = (colori+1)%len(colors)
            self.print_point(self.lidar.compute_center(shape), color='green')

        self.window.after(self.interface_refresh, self.update_interface)


    def close(self):
        del self.lidar
        super().close()
