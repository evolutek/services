#!/usr/bin/env python3
# Service: Timer
# Author: Rémi Audebert, <mail@halfr.net>

__version__ = "1"

import threading
import time

from cellaserv.service import Service

class Timer(Service):

    version = __version__

    def __init__(self):
        super().__init__()

        self.t = None
        self.started_at = 0

    # Actions

    @Service.action
    def start(self, duration):
        duration = float(duration)

        self.t = threading.Timer(duration, self.done)
        self.t.start()
        self.finish_time = time.time() + duration

    @Service.action
    def stop(self):
        if self.t:
            self.t.cancel()

    @Service.action
    def get_remaining(self):
        delta = self.finish_time - time.time()
        return max(delta, 0)

    # Events sent

    def done(self):
        data = None
        if self.identification:
            data = {"timer": self.identification}

        self.notify("timer-done", data)

def main():
    timer = Timer()
    timer.run()

if __name__ == "__main__":
    main()
