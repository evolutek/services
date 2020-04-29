#!/usr/bin/#!/usr/bin/env python3
from time import sleep

from evolutek.lib.rgb_sensors import RGBSensors

rgb = RGBSensors([1, 2])

while True:
    print('Sensor 1 Color: ({0}, {1}, {2})'.format(*rgb.read_sensor(1)))
    print('Sensor 2 Color: ({0}, {1}, {2})'.format(*rgb.read_sensor(2)))
    sleep(0.5)
