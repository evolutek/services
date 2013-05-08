#!/usr/bin/env python3
# Service: Timer
# Author: Samuel Angebault <staphyloa@gmail.com>

__version__ = "1"

import threading
import socket
from PIL import Image

from cellaserv.service import Service

class Camera(Service):

    version = __version__

    def __init__(self):
        super().__init__()
        self.ip = None
        self.port = None
        self.position = None

    def compute(self):
        result = "ok"
        try:
            s = socket.create_connection((self.ip, self.port))
            data = bytes()
            while True:
                tmp = s.recv(4096)
                if not tmp:
                    break
                data += tmp
            s.close()
            if len(data) == 0:
                return "error: retreiving"
            with open("/tmp/cake.jpg", "wb") as f:
                f.write(data)
            img = Image.open("/tmp/cake.jpg")
            print(img.size)
        except Exception as e:
            print(e)
            result = "error"
        self.notify("camera-result", {"result": result})

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
            return {"result": "error"}

        th = threading.Thread(None, self.compute, "computation")
        th.start()
        return {"result": "computing"}

def main():
    camera = Camera()
    camera.run()

if __name__ == "__main__":
    main()
