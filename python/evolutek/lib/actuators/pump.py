from evolutek.lib.component import Component, ComponentsHolder

class Pump(Component):
    def __init__(self, id, pump_gpio, ev_gpio):
        super().__init__('Pump', id)
        self.pump_gpio = pump_gpio
        self.ev_gpio = ev_gpio
        self.init = True

    def get(self):
        self.pump_gpio.write(True)
        if(self.ev_gpio is not None) :
            self.ev_gpio.write(False)

    def drop(self, use_ev=True):
        self.pump_gpio.write(False)
        if(self.ev_gpio is not None) :
            if use_ev: self.ev_gpio.write(True)

    def stop_ev(self):
        if(self.ev_gpio is not None) :
            self.ev_gpio.write(False)

    def __str__(self):
        s = "----------\n"
        s += "Pump: %d\n" % self.id
        s += "Pump output: %d\n" % self.pump_gpio.read()
        if(self.ev_gpio is not None) : s += "EV output: %d\n" % self.ev_gpio.read()
        s += "----------"
        return s

    def __dict__(self):
        if(self.ev_gpio is not None) :
            return {
                "name" : self.name,
                "id": self.id,
                "pump_output": self.pump_gpio.read(),
                "ev_output": self.ev_gpio.read()
            }
        else : 
            return {
                "name" : self.name,
                "id": self.id,
                "pump_output": self.pump_gpio.read(),
            }

class PumpController(ComponentsHolder):
    def __init__(self, pumps, valve_delay=None):
        super().__init__('Pump Controller', pumps, Pump)

    def gets(self, ids):
        for id in ids:
            if self.components[id] is None:
                continue
            self.components[id].get()

    def drops(self, ids, use_ev = False):
        for id in ids:
            if self.components[id] is None:
                continue
            self.components[id].drop(use_ev)

    def stop_evs(self, ids):
        for id in ids:
            if self.components[id] is None:
                continue
            self.components[id].stop_ev()
