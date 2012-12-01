#!/usr/bin/env python
import sys
import os

from cellaserv.proxy import CellaservProxy

def main():
    if len(sys.argv) < 2:
        print("Error: expect ax ids as argument", file=sys.stderr)
        sys.exit(1)

    cs = CellaservProxy()
    axs = [cs.ax[int(ax_id)] for ax_id in sys.argv[1:]]
    for ax in axs:
        print("AX {:3} Status".format(ax.identification))
        print("Position: {:4}".format(ax.get_present_position()))
        print("Voltage: {:4}".format(ax.get_present_voltage()))
        print("Temperature: {:4}".format(ax.get_present_temperature()))

if __name__ == '__main__':
    main()
