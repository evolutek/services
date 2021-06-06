from evolutek.lib.component import Component, ComponentsHolder

from time import sleep

DEFAULT_VALVE_DELAY = 0.25

class Pump(Component):
    def __init__(self, id, valve_delay, pump_gpio, ev_gpio):
        super().__init__('Pump', id)
        self.pump_gpio = pump_gpio
        self.ev_gpio = ev_gpio
        self.valve_delay = valve_delay if not valve_delay is None else DEFAULT_VALVE_DELAY

        self.init = True

    def get(self):
        self.pump_gpio.write(True)

    def drop(self):
        self.pump_gpio.write(False)
        self.ev_gpio.write(True)
        sleep(self.valve_delay)
        self.ev_gpio.write(False)

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
        super().__init__('Pump Controller', pumps, Pump, common_args=[valve_delay])
