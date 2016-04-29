#!/usr/bin/env python3

import mraa
from cellaserv.proxy import CellaservProxy
from cellaserv.protobuf.cellaserv_pb2 import Message
from cellaserv.service import Service

def test(args):
    print("foo")

class Tirette(Service):
    def ready_to_go(self, go_button):
        go = mraa.Gpio(go_button)
        go.dir(mraa.DIR_IN)

        print("Ready to go, awaiting...")

        value = go.read()

        while True:
            new_value = go.read()
            if (value != new_value):
                value = new_value
                if (value == 1):
                    self.publish("tirette_up")
                    print("tirette_up")
                else:
                    self.publish("tirette_down")
                    print("tirette_down")



    def set_color(self, color_button):
        color = mraa.Gpio(color_button)
        color.dir(mraa.DIR_IN)
        mycolor = 'yellow' if color.read() == 1 else 'green'
        self.publish('config.match.color', value = mycolor)

def main():
    tirette = Tirette()
    tirette.set_color(0)
    tirette.ready_to_go(2)

if __name__ == "__main__":
    main()
