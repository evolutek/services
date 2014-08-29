#!/usr/bin/env python3

import time

from cellaserv.service import Service


class Date(Service):

    @Service.action
    def time(self):
        return {'epoch': int(time.time())}

    @Service.event
    def kill(self):
        import sys
        sys.exit(0)


def main():
    date = Date()
    date.run()

if __name__ == "__main__":
    main()
