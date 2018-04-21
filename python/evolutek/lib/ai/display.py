from graph import *
from tkinter import *

class Interface:

  def __init__(self, graph, path, p):
    self.graph = graph
    self.path = path
    self.p = p
    print('Init interface')
    self.window = Tk()
    self.close_button = Button(self.window, text='Close', command=self.window.quit)
    self.close_button.pack()
    self.canvas = Canvas(self.window, width=1500, height=1000)
    self.map = PhotoImage(file='map.png')
    self.canvas.create_image(750, 500, image=self.map)
    self.canvas.pack()
    print('Window created')
    self.window.after(1000, self.update)
    self.window.mainloop()

  def print_node(self, node, name):
    self.canvas.create_oval((node.y/2)-20, (node.x/2)-20, (node.y/2)+20, \
      (node.x/2)+20, width=0, fill='red')
    self.canvas.create_text(node.y/2, node.x/2, text=name)

  def print_edges(self, node):
    for e in node[1]:
        point = self.graph.nodes[e[0]][0]
        self.canvas.create_line(node[0].y/2, node[0].x/2, point.y/2, point.x/2,\
          width=5, fill='green')

  def print_pal(self):
    self.canvas.create_rectangle((pal.y/2)-radius_pal, (pal.x/2)-radius_pal, \
      (pal.y/2)+radius_pal, (pal.x/2)+radius_pal, width=2, fill='orange')
    self.canvas.create_line(pal.y/2, pal.x/2, \
      (pal.y/2)+(radius_pal*cos(theta_pal-(pi/2))), \
      (pal.x/2)+(radius_pal*sin(theta_pal-(pi/2))), \
      width=5)

  def print_pmi(self):
    self.canvas.create_rectangle((pmi.y/2)-radius_pmi, (pmi.x/2)-radius_pmi, \
      (pmi.y/2)+radius_pmi, (pmi.x/2)+radius_pmi, width=2, fill='blue')
    self.canvas.create_line(pmi.y/2, pmi.x/2, \
      (pmi.y/2)+(radius_pmi*cos(theta_pmi-(pi/2))), \
      (pmi.x/2)+(radius_pmi*sin(theta_pmi-(pi/2))), \
      width=5)

  def print_path(self):
      for i in range(1, len(self.path)):
        curr = self.graph.nodes[self.path[i - 1]][0]
        next = self.graph.nodes[self.path[i]][0]
        self.canvas.create_line(curr.y/2, curr.x/2, next.y/2, next.x/2,\
          width=3, fill='purple')

  def print_line(self, p1, p2):
    self.canvas.create_line(p1.y/2, p1.x/2, p2.y/2, p2.x/2, width=2, fill='pink')

  def print_rectangle(self):
    self.print_node(self.p[0], "test")
    self.print_node(self.p[1], "test")
    self.print_node(self.p[2], "test")
    self.print_node(self.p[3], "test")
    self.print_line(self.p[0], self.p[2])
    self.print_line(self.p[2], self.p[3])
    self.print_line(self.p[3], self.p[1])
    self.print_line(self.p[1], self.p[0])

  def update(self):
    self.canvas.delete('all')
    self.canvas.create_image(750, 500, image=self.map)

    # Display edges
    for key, val in self.graph.nodes.items():
      self.print_edges(val)

    # Print path
    self.print_path()

    # Display nodes
    for key, val in self.graph.nodes.items():
      self.print_node(val[0], key)

    # Display robots
    self.print_pal()
    self.print_pmi()

    self.print_rectangle()

    self.window.after(1000, self.update)
