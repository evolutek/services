#!/usr/bin/env python3
# TODO: rewrite using cellaserv.service.Service
import time
import os
import ctypes

import cellaserv.client

AX_LOCATION = "./ax"

DXL_LOCATION = "./libdxl.so"
DEVICE_ID = 0
BAUD_RATE = 34
COMMAND_GOAL_POSITION_L = 30

class AbstractAxService(cellaserv.client.AsynClient):

    def __init__(self, sock):
        super().__init__(sock)

    def connect(self):
        self.register_service('ax')

    def message_recieved(self, message):
        if message['command'] == 'query' \
        and message['action'] == 'move' \
        and 'data' in message \
        and 'ax' in message['data'] \
        and 'goal' in message['data']:
            self.move(int(message['data']["ax"]), int(message['data']["goal"]))

            response = {}
            response['command'] = 'ack'
            response['id'] = message['id']

            self.send_message(response)

    def move(self, ax_id, goal):
        raise NotImplementedException

class SystemAxService(AbstractAxService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def move(self, ax_id, goal):
        os.system("{} {} {}".format(AX_LOCATION, ax_id, goal))

class CtypesService(AbstractAxService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.dxl = ctypes.CDLL(DXL_LOCATION)
        self.dxl.dxl_initialize(DEVICE_ID, BAUD_RATE)

    def __del__(self):
        self.dxl.dxl_terminate()

    def move(self, ax_id, goal):
        self.dxl.dxl_write_word(int(ax_id), COMMAND_GOAL_POSITION_L, int(goal))

def main():
    import asyncore
    import socket

    import local_settings

    HOST, PORT = local_settings.HOST, local_settings.PORT

    with socket.create_connection((HOST, PORT)) as sock:
        #service = SystemAxService(sock)
        service = CtypesService(sock)
        service.connect()

        asyncore.loop()

if __name__ == "__main__":
    main()
