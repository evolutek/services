#!/usr/bin/env python3

from cellaserv.service import Service
from time import sleep
from threading import Thread, Lock
import mraa

from evolutek.lib.settings import ROBOT

@Service.require("trajman", ROBOT)
class Gbts(Service):

    def __init__(self):
        super().__init__(ROBOT)
        self.front = mraa.Gpio(12)
        self.back = mraa.Gpio(13)
        self.front.dir(mraa.DIR_IN)
        self.back.dir(mraa.DIR_IN)
        self.front_avoid = False
        self.back_avoid = False
        self.enabled_avoiding = False
        self.lock = Lock()
        self.thread = Thread(target=self.main_loop)
        self.thread.start()

    def main_loop(self):
        while True:
            sleep(0.25)
            if not self.enabled_avoiding:
                continue

            front_value = self.front.read()
            back_value = self.back.read()

            with self.lock:
                if self.front_avoid and front_value == 0:
                    self.front_avoid = False
                    print("Front end_avoid")
                    self.publish("front_end_avoid")

                if self.back_avoid and back_value == 0:
                    self.back_avoid = False
                    print("Back end_avoid")
                    self.publish("back_end_avoid")

                if not self.front_avoid and front_value == 1:
                    self.front_avoid = True
                    print ('Front: avoid!')
                    self.publish("front_avoid")

                if not self.back_avoid and back_value == 1:
                    self.back_avoid = True
                    print ('Back: avoid!')
                    self.publish("back_avoid")

    # Set avoiding status
    @Service.action
    def set_avoiding(self, status=True):
        with self.lock:
            self.enabled_avoiding = status
            self.front_avoid = False
            self.back_avoid = False
            print('Avoing status: ' + str(self.enabled_avoiding))

def main():
    gbts = Gbts()
    gbts.run()

if __name__ == "__main__":
    main()
