#!/usr/bin/#!/usr/bin/env python3
from time import sleep

from evolutek.lib.rgb_sensors import RGBSensors

rgb = RGBSensors([2, 3])

print(rgb)

while True:
    print('Sensor 2 Color: ({0}, {1}, {2})'.format(*rgb.read_sensor(2)))
    print('Sensor 2 Color: %s)' % str(rgb.read_color(2)))
    print('Sensor 3 Color: ({0}, {1}, {2})'.format(*rgb.read_sensor(3)))
    print('Sensor 3 Color: %s)' % str(rgb.read_color(3)))
    sleep(1)
