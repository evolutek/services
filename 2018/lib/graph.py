from math import pow, sqrt, pi, cos, sin, atan, atan2

cost_stop = 100
cost_turn = 200
infinite = 100000

radius_pal = 215
radius_pmi = 150
radius_robot = 215

class Point:
  """
    A pair of cartesian coordinates (x, y)
  """

  def __init__(self, _x, _y):
    self.x = _x
    self.y = _y

  def __str__(self):
    return str(self.x) + ', ' + str(self.y)

  def to_dict(self):
      return {'x' : self.x, 'y' : self.y}

  def distance(self, point):
    """
      Returns the disnace to the point passed in argument
    """
    return sqrt(pow(self.x - point.x, 2) + pow(self.y - point.y, 2))

class Graph:
  """
    Required : class Point

    Implementation of non directed graph with linked lists (using Python dicts
    as lists).
    Nodes are named (dict key) and edges are weighted.

    #Point is the node named node_name
    graph nodes = {node_name : (Point, edges)

    #retrieves the dest point using its name
    edges = [(node_name, weight)]

  """

  def __init__(self):
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

  def is_colliding(self, circle, p1, p2):
    """
        Returns true if the circle collides with the rectange determined by two
        points which are the intersection between the rectangle and a meadian.
        This function unrotate the rectangle and then detect a potential collision.
        circle : center of the robot
        p1 : starting point of the path
        p2 : ending point of the path
    """
    width = pal_radius * 2
    height = p1.distance(p2)
    center = Point((p2.x + p1.x) / 2, (p2.y + p1.y) / 2)

    # compute the rotation angle of the circle
    coeff_x = (p2.y - p1.y) / (1 if p1.x == p2.x else p2.x - p1.x)

    rotation = atan(-coeff_x) - pi / 2

    # unrotated
    refx = center.x - width / 2
    refy = center.y - height / 2

    # unrotated circle
    unrotated_c = Point(cos(rotation) * (circle.x - center.x)   \
        - sin(rotation) * (circle.y - center.y) + center.x,     \
        sin(rotation) * (circle.x - center.x)                   \
        + cos(rotation) * (circle.y - center.y) + center.y)

    # closest unrotated point from center of unrotated circle
    closest = Point(unrotated_c.x, unrotated_c.y)

    if unrotated_c.x < refx:
        closest.x = refx
    elif unrotated_c.x > refx + width:
        closest.x = refx + width

    if unrotated_c.y < refy:
        closest.y = refy
    elif unrotated_c.y > refy + height:
        closest.y = refy + height

    # return if a collision occurs
    return unrotated_c.distance(closest) < radius_robot

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
    res.append((curr, self.nodes[curr][0].to_dict()))
    return list(reversed(res))
