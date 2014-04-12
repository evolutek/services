#!/usr/bin/env python3

from threading import Thread
import socket

from cellaserv.service import Service
from cellaserv.proxy import CellaservProxy

class Mbed(Service):

    def __init__(self):
        super().__init__()
        self.cs = CellaservProxy()

    def loop(self):
        HOST = ''
        PORT =  4201
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((HOST, PORT))
        s.listen(1)
        conn, addr = s.accept()
        self.cs('log.mbed', msg='Connected by {0}'.format(addr))

        counter = 0
        while True:
            # A message is 1 byte long
            data = conn.recv(1)
            if not data:
                self.cs('log.mbed', msg='Connection closed')
                break

            if data[0] == ord('G'):
                self.cs('match_start')
            elif data[0] == ord('1'):
                counter += 1
                if counter == 2:
                    self.cs('robot_near')
            elif data[0] == ord('0'):
                counter = 0
            else:
                self.cs('log.mbed', msg='Unknown data: {0}'.format(data))

def main():
    mbed = Mbed()
    t = Thread(target=mbed.loop)
    t.daemon = True
    t.start()
    mbed.run()

if __name__ == '__main__':
    main()
