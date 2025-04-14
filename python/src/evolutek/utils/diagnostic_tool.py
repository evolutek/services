#!/usr/bin/env python3

from cellaserv.proxy import CellaservProxy

import json
import os
from time import sleep

class DiagnosticTool:

    def __init__(self):

        connected = False

        while not connected:
            try:
                self.cs = CellaservProxy()
                connected = True
            except Exception as e:
                print('Failed to connected to cellaserv: %s' % str(e))

        config = None
        try:
            with open('/etc/conf.d/diagnostic.json', 'r') as file:
                data = file.read()
                config = json.loads(data)
        except Exception as e:
            print('Failed to read diagnostic config: %s' % str(e))
            return

        self.refresh = float(config['refresh'])
        self.services = config['services']
        self.devices = config['devices']

        print(self.devices)

    def make_diagnostic(self):

        print('---------------------')
        print('Making a diagnostic')

        print('-> Devices:')
        for device in self.devices:
            response = os.system("ping -c 1 -W 0.5 %s &> /dev/null" % device)
            print('%s: %s' % (device, 'connected' if response  == 0 else 'disconnected'))

        connected_services = self.cs.cellaserv.list_services()

        print('-> Services:')
        for service in self.services:
            connected = False

            for _service in connected_services:
                if _service['name'] == service['name'] and (not 'id' in service or _service['identification'] == _service['id']):
                    connected = True
                    break

            print('%s: %s' % (service['name'], 'connected' if connected else 'disconnected'))

def main():
    dt = DiagnosticTool()
    while True:
        dt.make_diagnostic()
        sleep(dt.refresh)

if __name__ == "__main__":
    main()
