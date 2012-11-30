#!/usr/bin/env python
# encoding: utf-8

from random import randint
from time import sleep
from cellaserv.proxy import CellaservProxy

def main():
    cs = CellaservProxy()
    while True:
        cs.ax("3").move(goal=randint(200, 800))
        sleep(0.5)
        cs.ax("5").move(goal=randint(200, 800))
        sleep(0.5)

if __name__ == '__main__':
    main()
