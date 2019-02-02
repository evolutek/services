#!/usr/bin/env python3

from cellaserv.service import Service, Event
from cellaserv.proxy import CellaservProxy
from evolutek.lib.settings import ROBOT
from evolutek.lib.tim import Tim
from threading import Lock
from time import sleep

def dist(a, b):
  return (a['x'] * b['x'] + a['y'] * b['y']) ** 0.5

@Service.require('config')
class Map(Service):

  def __init__(self):

    cs = CellaservProxy()

    self.color1 = cs.config.get(section='match', option='color1')
    self.color2 = cs.config.get(section='match', option='color2')

    self.delta_dist = float(cs.config.get(section='tim', option='delta_dist'))
    self.refresh = float(cs.config.get(section='tim', option='refresh'))

    self.tim_config = {
      'min_size' : float(cs.config.get(section='tim', option='min_size')),
      'max_distance' : float(cs.config.get(section='tim', option='max_distance')),
      'ip' : cs.config.get(section='tim', option='ip'),
      'port' : int(cs.config.get(section='tim', option='port')),
      'pos_x' : int(cs.config.get(section='tim', option='pos_x')),
      'pos_y' : int(cs.config.get(section='tim', option='pos_y')),
      'angle' : float(cs.config.get(section='tim', option='angle'))
    }
    
    self.lock = Lock()

    self.robots = []
    self.pal_telem = None

    self.color = None
    self.tim = None

    try:
      color = cs.match.get_color()
      self.match_color(color)
    except Exception as e:
      print('Failed to get color: %s' % str(e))

    super().__init__()
  
  @Service.event
  def match_color(self, color):
    if color != self.color:
      self.color = color
    if self.color is not None:
      config = self.tim_config
      if self.color != self.color1:
        config['pos_y'] = 3000 - config['pos_y']
        config['angle'] *= -1
      self.tim = Tim(config)
    else:
      self.tim = None

  @Service.event
  def pal_telemetry(self, status, telemetry):
    if status is not 'failed':
      self.pal_telem = telemetry

  @Service.thread
  def loop_scan(self):
    while True:
      if self.tim is None:
        print('TIM not connected')
        sleep(self.refresh)
        continue
      data = self.tim.get_scan()
      with self.lock:

        self.robots.clear()

        for point in data:
          # Check if point is not one of our robots
          if self.pal_telem and dist(self.pal_telem, point) < self.delta_dist:
            continue
          self.robots.append(point.to_dict())

        self.publish('oppenents', robots=self.robots)

      sleep(self.refresh)
"""
    @Service.action
    def get_optimal_goal(self, goals):
      optimum = None
      for goal in goals:
        option = dijkstra_path(goal)
        if optimum is None || option.cost < optimum.cost:
          # optimum -> Cfeate dict here

      return optimum
        
"""
if __name__ == '__main__':
  map = Map()
  map.run()
