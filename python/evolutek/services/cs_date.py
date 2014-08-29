#!/usr/bin/env python3

import time

from cellaserv.service import Service


class Date(Service):
    """The most useful service."""

    @Service.action
    def time(self):
        return {'epoch': int(time.time())}

    @Service.event
    def kill(self):
        """Kill the service"""
        import sys
        sys.exit(0)


def main():
    date = Date()
    date.run()

if __name__ == "__main__":
    main()
