#!/usr/bin/#!/usr/bin/env python3
from time import sleep

from evolutek.lib.rgb_sensors import RGBSensors

rgb = RGBSensors([2, 3], 10)

print(rgb)

while True:
    print('Sensor 2 Color: ({0}, {1}, {2})'.format(*rgb.read_sensor(2)))
    print('Sensor 2 Diff Colors: ({0}, {1}, {2})'.format(*rgb.get_diff_colors(2)))
    print('Sensor 3 Color: ({0}, {1}, {2})'.format(*rgb.read_sensor(3)))
    print('Sensor 3 Diff Colors: ({0}, {1}, {2})'.format(*rgb.get_diff_colors(3)))
    sleep(1)
