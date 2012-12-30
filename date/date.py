#!/usr/bin/env python3

__version__ = '1'
__variant__ = 'python'

import time

from cellaserv.service import Service

class DateService(Service):

    service_name = "date"
    version = __version__
    variant = __variant__

    @Service.action
    def time(self):
        return {'epoch': int(time.time())}

    @Service.event
    def kill(self):
        import sys
        sys.exit(0)

def main():
    date_service = DateService()
    date_service.run()

if __name__ == "__main__":
    main()
