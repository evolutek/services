#!/usr/bin/env python

from cellaserv.service import Service, ConfigVariable

class TestConfig(Service):
    foo = ConfigVariable("test", "foo")

    @Service.action
    def test(self):
        return self.foo()

def main():
    service = TestConfig()
    service.run()

if __name__ == '__main__':
    main()
