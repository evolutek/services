#!/usr/bin/env python3
# Service: Battery checker
# Author: Rémi Audebert, <mail@halfr.net>

import time
import fcntl
from sys import exit, stderr

from cellaserv.service import Service

ADC_BATTERY_CHANNEL = 6

# IOCTL
IOCTL_ADC_SET_CHANNEL = 0xc000fa01
IOCTL_ADC_SET_ADCTSC = 0xc000fa02

# MAGIC
RATE = 3.3 / 2**12 # 2**12 = resolution 3V3 max
MULTIPLIER = 2 # input tension is halved in order to be < 3V3

class Battery(Service):

    def __init__(self):
        super().__init__()

        self.fd = open('/dev/adc', 'rb')
        if not self.fd:
            print("Cannot open '/dev/adc/", file=stderr)
            exit(1)

        rv = fcntl.ioctl(self.fd, IOCTL_ADC_SET_CHANNEL,
                ADC_BATTERY_CHANNEL)
        if rv < 0:
            print("Cannot set channel for '/dev/adc'", file=stderr)
            exit(1)

    @Service.action
    def voltage(self):
        buf = b''
        while b'\n' not in buf:
            buf = self.fd.read(1)     # strip garbage

        buf = self.fd.read(5)         # 5 bytes -> 2**12 = "4096" + '\n'
        # buf = b'1234\n' or buf = b'0\n0\n0'
        string = buf.decode()         # bytes -> str
        samples = string.strip().splitlines() # samples = ['1234'] or
                                      # samples = ['0','0','0']
        val = int(samples[0])         # take the first one

        return val * RATE * MULTIPLIER

def main():
    battery = Battery()
    battery.run()

if __name__ == "__main__":
    main()
