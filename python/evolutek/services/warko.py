#!/usr/bin/env python3

from cellaserv.service import Service

class Warko(Service):

    def __init__(self):
        super().__init__()
        print("Hello from Warko")

    @Service.action
    def salute(self):
        return ("hi, how are u ?")

    @Service.event
    def match_start(self):
        print("match start")


def main():
    boi = Warko()
    boi.run()

if __name__ == "__main__":
    main()
