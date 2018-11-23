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
        go = mraa.Aio(go_button)
        go_value = go.readFloat()
        while(go_value < 1.0):
            sleep(0.5)
            print("Put the tirette")
            new_value = go.readFloat()
            if (go_value < new_value):
                go_value = new_value
        print("Ready to go, awaiting...")

        while True:
            sleep(0.5)
            new_value = go.readFloat()
            if (go_value > new_value):
                go_value = new_value
                if (go_value == 0.0):
                    self.publish("match_start")
                    print("Match start")

    def set_color(self, color_button):
        color = mraa.Aio(color_button)
        mycolor = 'green' if color.readFloat() < 1.0 else 'orange'
        print("Color = " + mycolor)
        self.cs.config.set(section="match", option="color", value=mycolor)

def main():
    tirette = Tirette()
    tirette.set_color(1)
    tirette.ready_to_go(0)

if __name__ == "__main__":
    main()
