#!/usr/bin/env python
# encoding: utf-8

import sys
from random import randint
from time import sleep
from cellaserv.proxy import CellaservProxy

def main():
    if len(sys.argv) < 2:
        print("Error: expect ax ids as argument", file=sys.stderr)
        sys.exit(1)

    cs = CellaservProxy()
    axs = [cs.ax[ax_id] for ax_id in sys.argv[1:]]
    while True:
        for ax in axs:
            ax.move(goal=randint(200, 800))

if __name__ == '__main__':
    main()
