#!/usr/bin/env python3
# Service: Timer
# Author: Samuel Angebault <staphyloa@gmail.com>

__version__ = "1"

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
            return "error"
        s = socket.create_connection((self.ip, self.port))
        data = []
        while True:
            tmp = s.recv(4096)
            if not tmp:
                break
            data.append(tmp)
        res = [item for sublist in data for item in sublist]
        s.close()
        img = Image.fromstring(res)
        print(img.size)


    # Events sent
    def done(self):
        data = None
        if self.identification:
            data = {"camera": self.identification}

        self.notify("process-done", data)

def main():
    camera = Camera()
    camera.run()

if __name__ == "__main__":
    main()
