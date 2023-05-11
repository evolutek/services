import json
from os import system
from time import sleep

from cellaserv.service import Service

from evolutek.lib.gpio.gpio_factory import GpioType, create_gpio
from evolutek.lib.gpio.gpio import Edge
from evolutek.lib.settings import ROBOT

FILEPATH = "/etc/conf.d/reset.json"

#TODO :
# - Get status

class Reset(Service):

    def __init__(self):

        self.services = []
        if not self.parse_config():
            raise Exception('Error during parsing')

        self.reset = create_gpio(21, 'reset', dir=False, edge=Edge.RISING, type=GpioType.RPI)
        self.reset.auto_refresh(refresh=0.5, callback=self._reset)
        self.reset_soft = create_gpio(26, 'reset_soft', dir=True, default_value=False, type=GpioType.RPI)

        super().__init__(ROBOT)

        def parse_config(self):
            data = None
            try:
                with open(FILEPATH, 'r') as config:
                    data = config.read()
            except Exception as e:
                print('[RESET] Failed to read file: %s' % str(e))
                return False

            config = json.loads(data)
            try:
                self.services = config[ROBOT]
            except Exception as e:
                print('[RESET] Failed to get services: %s' % str(e))
                return False

            return True

    @Service.event('reset-%s' % ROBOT)
    @Service.event('reset-all')
    @Service.action()
    def reset(self):
        print('[RESET] Toggling software reset')
        self.reset_soft.write(True)
        sleep(1)
        self.reset_soft.write(False)

    def _reset(self):
        print('[RESET] Resetting all services')
        for service in self.services:
            system('sudo systemctl restart %s' % service)

def main():
    reset = Reset()
    reset.run()

if __name__ == '__main__':
    main()
