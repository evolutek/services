from evolutek.lib.component import Component, ComponentsHolder

class ProximitySensor(Component):

    def __init__(self, id, gpio):
        self.gpio = gpio
        super().__init__('Proximity sensor', id)

    def read(self):
        return self.gpio.read()

    def __str__(self):
        s = "----------\n"
        s += "Proximy sensor: %d\n" % self.id
        s += "Detection: %d\n" % self.read()
        s += "----------"
        return s

    def __dict__(self):
        return {
            "name" : self.name,
            "id" : self.id,
            "detection": self.read()
        }

class ProximitySensors(ComponentsHolder):

    def __init__(self, sensors):
        super().__init__('Proximity sensors', sensors, ProximitySensor)

    def read_all_sensors(self):
        results = {}
        for sensor in self.components:
            results[sensor] = self.components[sensor].read()
        return results
