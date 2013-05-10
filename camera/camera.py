#!/usr/bin/env python3
# Service: Timer
# Author: Samuel Angebault <staphyloa@gmail.com>

__version__ = "1"

import threading
import socket
import json

from cellaserv.service import Service

default = { top:"B??????R", bottom:"B???WWWW???R" }

class Camera(Service):

    version = __version__

    def __init__(self):
        super().__init__()
        self.ip = None
        self.port = None
        self.position = None

    def compute(self):
        try:
            s = socket.create_connection((self.ip, self.port))
            data = ""
            while True:
                tmp = str(s.recv(4096), 'ascii')
                if not tmp:
                    break
                data += tmp
            s.close()
            if len(data) == 0:
                raise InputError("read", "read result failed")
            self.notify("camera-result", { "result": "ok", "data": json.loads(data) })
        except Exception as e:
            self.notify("camera-result", { "result": "error", "data": default })

    # Actions
    @Service.action
    def start(self, position):
        self.position = position

    @Service.action
    def set_device(self, ip, port):
        self.ip = ip
        self.port = port

    @Service.action
    def process(self):
        # position to know where we start
        if not self.port or not self.ip or not self.position:
            return { "result": "default", "data": default }

        th = threading.Thread(None, self.compute, "computation")
        th.start()
        return {"result": "computing"}

def main():
    camera = Camera()
    camera.run()

if __name__ == "__main__":
    main()
