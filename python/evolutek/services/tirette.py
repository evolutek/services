#!/usr/bin/env python3

import mraa
from time import sleep
from cellaserv.proxy import CellaservProxy
from cellaserv.protobuf.cellaserv_pb2 import Message
from cellaserv.service import Service

@Service.require("config")
class Tirette(Service):

    def __init__(self):
        super().__init__()
        self.cs = CellaservProxy()

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

    def set_color(self, color_button):
        color = mraa.Gpio(color_button)
        color.dir(mraa.DIR_IN)
        mycolor = 'green' if color.read() == 1 else 'orange'
        print("Color = " + mycolor)
        self.cs.config.set(section="match", option="color", value=mycolor)

def main():
    tirette = Tirette()
    tirette.set_color(5)
    tirette.ready_to_go(10)

if __name__ == "__main__":
    main()
