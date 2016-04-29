#!/usr/bin/env python

from cellaserv.service import Service


class Echo(Service):

    @Service.action
    def echo(self, *args, **kwargs):
        """Returns its arguments."""
        return (args, kwargs)


def main():
    echo = Echo()
    echo.run()

if __name__ == '__main__':
    main()
