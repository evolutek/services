from math import pow, sqrt

infinite = 100000

class Point:
  def __init__(self, _x, _y):
    self.x = _x
    self.y = _y

  def __str__(self):
    return str(self.x) + ', ' + str(self.y)

  def distance(self, point):
    return sqrt(pow(self.x - point.x, 2) + pow(self.y - point.y, 2))

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

  def insert_node(self, name, x, y):
    p = Point(x, y)
    self.nodes[name] = (p, [])

  def insert_edges(self, src_name, dests_names):
    if src_name in self.nodes:
      src_point, src_edges = self.nodes[src_name]
      for dest_name in dests_names:
        if dest_name in self.nodes:
          dest_point, dest_edges = self.nodes[dest_name]
          weight = src_point.distance(dest_point)
          src_edges.append((dest_name, weight))
          dest_edges.append((src_name, weight))

  def cost(self, prec_name, curr_name, dest_name):
    if curr_name == dest_name:
      return 0

    return next(x[1] for x in self.nodes[curr_name][1] if x[0] == dest_name)

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

g = Graph()
g.insert_node('A', 0, 0)
g.insert_node('B', 10, 0)
g.insert_node('C', 0, 10)
g.insert_node('D', 10, 10)
print('Before adding edges')
print(str(g))
g.insert_edges('A', [ 'C', 'D'])
g.insert_edges('B', ['C', 'D'])
g.insert_edges('C', ['D'])
print('After adding edges')
print(str(g))

print(g.get_path('A', 'B'))
