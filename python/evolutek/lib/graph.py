from math import pow, sqrt, pi, cos, sin, atan2
from tkinter import *

cost_stop = 100
cost_turn = 200
infinite = 100000

radius_pal = 75
radius_pmi = 53

class Point:

  def __init__(self, _x, _y):
    self.x = _x
    self.y = _y

  def __str__(self):
    return str(self.x) + ', ' + str(self.y)

  def distance(self, point):
    return sqrt(pow(self.x - point.x, 2) + pow(self.y - point.y, 2))

pal = Point(500, 2760)
pmi = Point(200, 2760)
theta_pal = -pi/2
theta_pmi = -pi/2

class Interface:

  def __init__(self, graph, path):
    self.graph = graph
    self.path = path
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
          width=1, fill='orange')

  def update(self):
    print('Updating window')
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

    self.window.after(1000, self.update)

class Graph:

  def __init__(self):
    """
    edges = [(node_name, weight)]
    nodes = {node_name : (Point, edges)}
    """
    self.nodes = {}

  def __str__(self):
    s = ''
    for key, val in self.nodes.items():
      s += key + ': ' + str(val[0]) + '\n'
      for node, weight in val[1]:
        s += '\t-> ' + node + ': ' + str(weight) + '\n'
    return s

  def insert_node(self, name, x, y, color='green'):
    p = Point(x, y if color == 'orange' else 3000 - y)
    self.nodes[name] = (p, [])

  def insert_edges(self, src_name, dests_names):
    if src_name in self.nodes:
      src_point, src_edges = self.nodes[src_name]
      for dest_name in dests_names:
        if dest_name in self.nodes \
	  and dest_name not in [x[0] for x in src_edges]:
          dest_point, dest_edges = self.nodes[dest_name]
          weight = src_point.distance(dest_point)
          src_edges.append((dest_name, weight))
          dest_edges.append((src_name, weight))

  def cost(self, prec_name, curr_name, dest_name):
    if curr_name == dest_name:
      return 0

    ptx = self.nodes[prec_name][0]
    pty = self.nodes[curr_name][0]
    ptz = self.nodes[dest_name][0]

    angle = abs((atan2(ptx.x - pty.x, ptx.y - pty.y) \
      - atan2(ptz.x - pty.x, ptz.y - pty.y)))

    return next(x[1] for x in self.nodes[curr_name][1] if x[0] == dest_name) \
           + cost_stop + (angle * cost_turn)

  def find_closest(self, shortest_paths, every_nodes):
    minimum = infinite
    res = -1
    for i in range(len(every_nodes)):
      node_name = every_nodes[i][0]
      if shortest_paths[node_name] < minimum :
        minimum = shortest_paths[node_name]
        res = i
    return res

  def update_precs(self, src_name, dst_name, shortest_paths, precs):
    weight = self.cost(precs[src_name], src_name, dst_name)
    if shortest_paths[dst_name] > shortest_paths[src_name] + weight:
      shortest_paths[dst_name] = shortest_paths[src_name] + weight
      precs[dst_name] = src_name

  def get_path(self, src_name, dest_name):

    # initialisation
    shortest_paths = {}
    precs = {}
    for name, val in self.nodes.items():
      shortest_paths[name] = infinite
    shortest_paths[src_name] = 0
    precs[src_name] = src_name

    # dijkstra
    every_nodes = list(self.nodes.items())
    while len(every_nodes):
      s1 = self.find_closest(shortest_paths, every_nodes)
      node_name, node_val = list(every_nodes[s1])
      every_nodes.pop(s1)
      for dest, weight in node_val[1]:
        self.update_precs(node_name, dest, shortest_paths, precs)

    # get the path
    res = []
    curr = dest_name

    while curr != src_name:
      res.append(curr)
      curr = precs[curr]
    res.append(curr)
    return list(reversed(res))

def get_map(color):

    map = Graph()

    # Add nodes
    map.insert_node('start', 500, 2760, color)
    map.insert_node('bee', 1750, 2750, color)
    map.insert_node('construction', 350, 2390, color)
    map.insert_node('distrib1', 840, 2390, color)
    map.insert_node('distrib2', 1550, 2390, color)
    map.insert_node('interrupteur', 350, 1870, color)
    map.insert_node('center_interrupter', 350, 1500, color)
    map.insert_node('inter_a', 840, 1870, color)
    map.insert_node('inter_b', 840, 1130, color)
    map.insert_node('center_balls', 1550, 1500, color)
    map.insert_node('center', 1000, 1500, color)
    map.insert_node('distrib3', 840, 610, color)
    map.insert_node('distrib4', 1550, 610, color)

    # Add edges
    map.insert_edges('start', ['construction', 'distrib1', 'distrib4'])
    map.insert_edges('bee', ['distrib2', 'inter_a', 'center_interrupter', 'center'])
    map.insert_edges('construction', ['distrib1', 'interrupteur', 'distrib2', 'center_interrupter'])
    map.insert_edges('distrib1', ['distrib2', 'inter_a', 'center', 'inter_b', 'distrib3'])
    map.insert_edges('distrib2', ['inter_a', 'center', 'center_interrupter'])
    map.insert_edges('interrupteur', ['center_interrupter', 'center_balls', 'inter_a', 'center', 'inter_b', 'distrib3', 'distrib4'])
    map.insert_edges('center_interrupter', ['center_balls', 'inter_a', 'center', 'inter_b', 'distrib4'])
    map.insert_edges('inter_a', ['center_balls', 'center', 'inter_b', 'distrib3', 'distrib4'])
    map.insert_edges('inter_b', ['center_balls', 'center', 'distrib3', 'distrib4'])
    map.insert_edges('center_balls', ['center'])
    map.insert_edges('distrib3', ['distrib4', 'center'])
    map.insert_edges('distrib4', ['center'])

    return map

def main():
  print('Test')
  map = get_map('orange')
  curr_path = map.get_path('start', 'bee')
  interface = Interface(map, curr_path)

if __name__ == '__main__':
    main()
