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

    self.delta_dist = float(cs.config.get(section='tim', option='delta_dist'))
    self.refresh = float(cs.config.get(section='tim', option='refresh'))

    self.tim_config = {
      'min_size' : float(cs.config.get(section='tim', option='min_size')),
      'max_distance' : float(cs.config.get(section='tim', option='max_distance')),
      'ip' : cs.config.get(section='tim', option='ip'),
      'port' : int(cs.config.get(section='tim', option='port')),
      'pos_x' : int(cs.config.get(section='tim', option='pos_x')),
      'pos_y' : int(cs.config.get(section='tim', option='pos_y')),
      'angle' : float(cs.config.get(section='tim', option='max_distance'))
    }
    
    self.lock = Lock()

    self.robots = []
    self.pal_telem = None

    self.tim = Tim(self.tim_config)

    super().__init__()

  @Service.event
  def pal_telemetry(self, status, telemetry):
    if status is not 'failed':
      self.pal_telem = telemetry

  @Service.thread
  def loop_scan(self):
    if not self.tim.connected:
      print('TIM not connected')
      return
    while True:
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

if __name__ == '__main__':
  map = Map()
  map.run()
