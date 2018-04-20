from point import *
from graph import *
from display import *

def get_map(color):
  """
    Returns the basic graph for the 2017/2018 competition.
    this graph is meant for testing the implementation of the ai algorithms.
  """

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
  p = map.collision(None, map.nodes['start'][0], map.nodes['distrib1'][0])
  interface = Interface(map, curr_path, p)

  p1 = Point(100,100)
  p2 = Point(500, 500)

  collision = True
  for i in range(1000):
    collision = collide_orectangle_circle(Point(i, 250), 50, p1, p2, 100)

if __name__ == '__main__':
  main()
