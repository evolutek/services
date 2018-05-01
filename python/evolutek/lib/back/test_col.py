from point import *
from graph import *
from tkinter import *

class Col_tester:

  def __init__(self, graph):
    self.p1 = Point(1500, 1500)
    self.p2 = Point(1000, 1500)

    coeff_x = (self.p2.y - self.p1.y) /  (1 if self.p1.x == self.p2.x else self.p2.x - self.p1.x)
    ordo = self.p1.y - coeff_x * self.p1.x
    angle = atan(coeff_x) - pi/2

    """
    if self.p1.x > self.p2.x:
        x = self.p1.x - radius_robot * cos(angle)
        self.p1 = Point(x, x * coeff_x + ordo)
        x = self.p2.x + radius_robot * cos(angle)
        self.p2 = Point(x, x * coeff_x + ordo)
    else:
        x = self.p1.x + radius_robot * cos(angle)
        self.p1 = Point(x, x * coeff_x + ordo)
        x = self.p2.x - radius_robot * cos(angle)
        self.p2 = Point(x, x * coeff_x + ordo)
    """

    self.p11 = Point(self.p1.x + (radius_robot * cos(angle)),
      self.p1.y + (radius_robot * sin(angle)))
    self.p12 = Point(self.p1.x - (radius_robot * cos(angle)),
      self.p1.y - (radius_robot * sin(angle)))
    self.p21 = Point(self.p2.x + (radius_robot * cos(angle)),
      self.p2.y + (radius_robot * sin(angle)))
    self.p22 = Point(self.p2.x - (radius_robot * cos(angle)),
      self.p2.y - (radius_robot * sin(angle)))


    self.graph = graph
    print('Init interface')
    self.window = Tk()
    self.close_button = Button(self.window, text='Close', command=self.window.quit)
    self.close_button.pack()
    self.canvas = Canvas(self.window, width=1500, height=1000)
    self.map = PhotoImage(file='map.png')
    self.canvas.create_image(750, 500, image=self.map)
    self.canvas.pack()

    self.counter = 21
    self.way = 20

    print('Window created')
    self.window.after(1000, self.update)
    self.window.mainloop()

  def print_node(self, node, name, r, is_col):
    if is_col:
      self.canvas.create_oval((node.y/2)-r, (node.x/2)-r, (node.y/2)+r, \
        (node.x/2)+r, width=0, fill='red')

    else :
      self.canvas.create_oval((node.y/2)-r, (node.x/2)-r, (node.y/2)+r, \
        (node.x/2)+r, width=0, fill='green')

    self.canvas.create_text(node.y/2, node.x/2, text=name)

  def print_edges(self, node):
    for e in node[1]:
        point = self.graph.nodes[e[0]][0]
        self.canvas.create_line(node[0].y/2, node[0].x/2, point.y/2, point.x/2,\
          width=5, fill='green')


  def print_line(self, p1, p2):
    self.canvas.create_line(p1.y/2, p1.x/2, p2.y/2, p2.x/2, width=5, fill='orange')

  def print_rectangle(self, p):
    #self.print_node(p[0], "test")
    #self.print_node(p[1], "test")
    #self.print_node(p[2], "test")
    #self.print_node(p[3], "test")
    self.print_line(p[0], p[2])
    self.print_line(p[2], p[3])
    self.print_line(p[3], p[1])
    self.print_line(p[1], p[0])

  def update(self):
    self.canvas.delete('all')
    self.canvas.create_image(750, 500, image=self.map)


    for i in range(0, 2000, 50):
      for j in range(0, 3000, 50):
        p = Point(i, j)
        collision = collide_orectangle_circle(p, 2, self.p1, self.p2, radius_robot)
        self.print_node(p, '', 2, collision)

    #self.print_node(self.p1, 'A', 10, False)
    #self.print_node(self.p2, 'B', 10, False)

    p = Point(self.counter, 750)
    collider_r = 150
    collision = collide_orectangle_circle(p, collider_r, self.p1, self.p2, radius_robot)
    self.print_node(p, 'robot', collider_r / 2, collision)

    self.print_rectangle([self.p11, self.p12, self.p21, self.p22])

    if (self.counter + self.way > 1450 or self.counter + self.way < 20) :
      self.way *= -1

    self.counter += self.way

    self.window.after(200, self.update)

map = Graph()
map.insert_node('A', 900, 500, 'orange')
map.insert_node('B', 1000, 1000, 'orange')
tester = Col_tester(map)
