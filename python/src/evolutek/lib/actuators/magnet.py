from evolutek.lib.component import Component, ComponentsHolder

class Magnet(Component):
    def __init__(self, id, gpio):
        super().__init__('Pump', id)
        self.gpio = gpio
        self.init = True

    def on(self):
        self.gpio.write(True)

    def off(self):
        self.gpio.write(False)

    def __str__(self):
        s = "----------\n"
        s += "Magnet: %d\n" % self.id
        s += "Stats: %d\n" % self.gpio.read()
        s += "----------"
        return s

    def __dict__(self):
        return {
            "name" : self.name,
            "id": self.id,
            "stats": self.gpio.read()
        }

class MagnetController(ComponentsHolder):
    def __init__(self, magnets):
        super().__init__('Magnet Controller', magnets, Magnet)

    def on(self, ids):
        for id in ids:
            if self.components[id] is None:
                continue
            self.components[id].on()

    def off(self, ids):
        for id in ids:
            if self.components[id] is None:
                continue
            self.components[id].off()

    def free(self):
        for magnet in self.components.values():
            try:
                magnet.off()
            except Exception as e:
                print(e)
