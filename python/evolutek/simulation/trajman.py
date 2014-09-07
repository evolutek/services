#!/usr/bin/env python3

from enum import IntEnum
from struct import pack, unpack
import os
import pty

from cellaserv.service import Service
from cellaserv.settings import DEBUG

from evolutek.lib.map import Vector3
from evolutek.lib.settings import ROBOT


class SerialCommand(IntEnum):
    get_position = 12

    get_vector_trsl = 16

    goto_xy = 100
    goto_theta = 101

    set_pid_trsl = 150
    set_pid_rot = 151

    set_trsl_acc = 152
    set_trsl_dec = 153
    set_trsl_maxspeed = 154

    set_rot_acc = 155
    set_rot_dec = 156
    set_rot_maxspeed = 157

    set_wheels_diam = 161
    set_wheels_spacing = 162

    set_delta_max_rot = 163
    set_delta_max_trsl = 164

    ack = 200

    init = 254
    error = 255

    not_implemented = 256

COMMANDS_ACK = [
    SerialCommand.set_pid_trsl,
    SerialCommand.set_pid_rot,

    SerialCommand.set_trsl_acc,
    SerialCommand.set_trsl_dec,
    SerialCommand.set_trsl_maxspeed,

    SerialCommand.set_rot_acc,
    SerialCommand.set_rot_dec,
    SerialCommand.set_rot_maxspeed,

    SerialCommand.set_wheels_diam,
    SerialCommand.set_wheels_spacing,

    SerialCommand.set_delta_max_rot,
    SerialCommand.set_delta_max_trsl,
]


class MockMotorCard(Service):
    def __init__(self, pty_fd):
        self.pty_fd = pty_fd
        self.i = 0

        self.pos = Vector3(1500, 1000, 0)  # Center of the map
        self.vector_trsl = 1.0

        super().__init__()

    def print(self, *args):
        print(*args, sep='\t')

    def debug(self, *args):
        if DEBUG >= 1:
            self.print(args)

    def read(self, length=1):
        ret = bytes()
        while length >= 1:
            read = os.read(self.pty_fd, length)
            length -= len(read)
            ret += read
        return ret

    def write(self, data):
        os.write(self.pty_fd, data)

    @Service.thread
    def loop(self):
        while True:
            self.read_message()
            self.i += 1

    def read_message(self):
        pkt_len = self.read()[0]
        self.debug(self.i, "Packet length:", pkt_len)
        pkt_id = self.read()[0]
        try:
            pkt_cmd = SerialCommand(pkt_id)
        except:
            pkt_cmd = SerialCommand.not_implemented
        pkt_data = self.read(pkt_len - 2)
        self.debug(self.i, "Packet ID:", pkt_id)
        self.debug(self.i, "Packet data:", pkt_data)

        getattr(self, 'do_' + pkt_cmd.name)(pkt_id, pkt_data)

    # Protocol implementation

    def ack(self):
        self.write(bytes([2, SerialCommand.ack]))

    for cmd in COMMANDS_ACK:
        exec("""
def do_{name}(self, pkt_id, data):
    self.print("STUB: {name:20}", data)
    self.ack()
""".format(name=cmd.name))

    def do_goto_xy(self, pkt_id, data):
        x, y = unpack('ff', data)
        self.pos = self.pos._replace(x=x, y=y)
        self.publish('log.{}.position'.format(ROBOT),
                     x=self.pos.x,
                     y=self.pos.y,
                     theta=self.pos.theta)
        self.ack()

    def do_goto_theta(self, pkt_id, data):
        [theta] = unpack('f', data)
        self.pos = self.pos._replace(theta=theta)
        self.publish('log.{}.position'.format(ROBOT),
                     x=self.pos.x,
                     y=self.pos.y,
                     theta=self.pos.theta)
        self.ack()

    def do_get_position(self, pkt_id, data):
        data = pack('=bfff', pkt_id, self.pos.x, self.pos.y, self.pos.theta)
        self.write(pack('b', 1 + len(data)))
        self.write(data)

    def do_get_vector_trsl(self, pkt_id, data):
        data = pack('=bf', pkt_id, self.vector_trsl)
        self.write(pack('b', 1 + len(data)))
        self.write(data)

    def do_init(self, pkt_id, data):
        self.print("INIT")

    def do_not_implemented(self, pkt_id, data):
        self.print("NOT IMPLEMENTED", pkt_id, data)


def main():
    master, slave = pty.openpty()
    print("Start trajman.py using serial port: ", os.ttyname(slave))

    motor_card = MockMotorCard(master)
    motor_card.run()

if __name__ == '__main__':
    main()
