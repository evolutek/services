from evolutek.lib.component import Component, ComponentsHolder

from time import sleep

DEFAULT_VALVE_DELAY = 1

class Pump(Component):
    def __init__(self, id, pump_gpio, ev_gpio):
        super().__init__('Pump', id)
        self.pump_gpio = pump_gpio
        self.ev_gpio = ev_gpio
        self.init = True

    def get(self):
        self.pump_gpio.write(True)

    def __str__(self):
        s = "----------\n"
        s += "Pump: %d\n" % self.id
        s += "Pump output: %d\n" % self.pump_gpio.read()
        s += "EV output: %d\n" % self.ev_gpio.read()
        s += "----------"
        return s

    def __dict__(self):
        return {
            "name" : self.name,
            "id": self.id,
            "pump_output": self.pump_gpio.read(),
            "ev_output": self.ev_gpio.read()
        }

class PumpController(ComponentsHolder):

    def __init__(self, pumps, valve_delay=None):
        super().__init__('Pump Controller', pumps, Pump)
        self.valve_delay = DEFAULT_VALVE_DELAY if valve_delay is None else valve_delay

    def drops(self, ids):
        for id in ids:
            if self.components[id] is None:
                continue
            self.components[id].pump_gpio.write(False)
            self.components[id].ev_gpio.write(True)

        sleep(self.valve_delay)

        for id in ids:
            if self.components[id] is None:
                continue
            self.components[id].ev_gpio.write(False)
