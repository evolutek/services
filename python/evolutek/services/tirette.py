#!/usr/bin/env python3



import mraa
from cellaserv.proxy import CellaservProxy
from cellaserv.protobuf.cellaserv_pb2 import Message
from cellaserv.service import Service


class Tirette(Service):
    
    def ready_to_go(self, go_button): 
        go = mraa.Gpio(go_button)
        go.dir(mraa.DIR_IN)

        print("Ready to go, awaiting...")
        go.isr(mraa.EDGE_BOTH, say_go)

    def say_go(self):
        self.publish('start')
        print("For the king, for the order !")
    
    def set_color(self, color_button):
        color = mraa.Gpio(color_button)
        color.dir(mraa.DIR_IN)
        mycolor = 'yellow' if color.read() == 1 else 'green'
        self.publish('config.match.color', value = mycolor)

def main():
    tirette = Tirette()
    tirette.set_color(0)
    tirette.ready_to_go(1)

if __name__ == "__main__:
    main()
    
