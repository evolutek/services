#!/bin/python3



from math import cos, sin, pi
from sys import argv

#print(float(argv[1]) + cos(float(argv[3])) * float(argv[4]), float(argv[2]) + sin(float(argv[3])) * float(argv[4]))
for i in range(8):
    print(1050 + cos(pi/4 * i) * 400, 1500 + sin(pi/4 * i) * 400, pi - pi/8*i)

