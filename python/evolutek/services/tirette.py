#!/usr/bin/env python3

import mraa
from time import sleep
from cellaserv.proxy import CellaservProxy
from cellaserv.protobuf.cellaserv_pb2 import Message
from cellaserv.service import Service

class Tirette(Service):

    def ready_to_go(self, go_button):
        go = mraa.Gpio(go_button)
        go.dir(mraa.DIR_IN)
        go_value = go.read()
        while(go_value != 1):
            sleep(1)
            print("Put the tirette")
            sleep(1)
            new_value = go.read()
            if (go_value != new_value):
                go_value = new_value
        print("Ready to go, awaiting...")

        while True:
            sleep(1)
            new_value = go.read()
            if (go_value != new_value):
                go_value = new_value
                if (go_value != 1):
                    self.publish("match_start")
                    print("Match start")

    def set_pattern(self, potentiometer):
        poten = mraa.Aio(potentiometer)
        poten_value = poten.readFloat()
        pattern = 0
        if poten_value < 0.2:
            pattern = 1
        elif poten_value < 0.4:
            pattern = 2
        elif poten_value < 0.6:
            pattern = 3
        elif poten_value < 0.8:
            pattern = 4
        else :
            pattern = 5
        print("Pattern = " + str(pattern))
        self.publish('config.match.pattern', value = pattern)


    def set_color(self, color_button):
        color = mraa.Gpio(color_button)
        color.dir(mraa.DIR_IN)
        mycolor = 'green' if color.read() == 1 else 'violet'
        print("Color = " + mycolor)
        self.publish('config.match.color', value = mycolor)

def main():
    tirette = Tirette()
    tirette.set_color(5)
    tirette.set_pattern(0)
    tirette.ready_to_go(2)

if __name__ == "__main__":
    main()
