#!/usr/bin/env python3

from cellaserv.service import Service

import mraa

class Gpios(Service):

    def __init__(self):
        super().__init__(identification=str('pal'))
        print('Init done')

    @Service.action
    def SetGpioIn(self, n=0):
        mraa.Gpio(n).dir(mraa.DIR_IN)

    @Service.action
    def SetGpioOut(self, n=0):
        mraa.Gpio(n).dir(mraa.DIR_OUT)

    # Read and Wrtie methods

    @Service.action
    def ReadAio(self, n=0):
        return mraa.Aio(n).readFloat()

    @Service.action
    def ReadGpio(self, n=0):
        return mraa.Gpio(n).read()

    @Service.action
    def WriteGpio(self, n=0, out=0):
        mraa.Gpio(n).write(out)

    @Service.action
    def WritePwm(self, n=0, out=0):
        mraa.Pwm(n).write(out)

def main():
    gpios = Gpios()
    Service.loop()

if __name__ == '__main__':
    main()
