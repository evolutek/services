from evolutek.lib.component import Component, ComponentsHolder
from evolutek.lib.utils.color import Color

class TryOhm(Component):

    def __init__(self, id, gpioa, gpiob):
        self.gpioa = gpioa
        self.gpiob = gpiob
        super().__init__('TryOhm sensor', id)

    def read(self):
        a = self.gpioa.read()
        b = self.gpiob.read()

        if a and b:
            return Color.Purple
        elif a:
            return Color.Red
        elif b:
            return Color.Yellow
        else:
            return Color.Unknown

    def __str__(self):
        s = "----------\n"
        s += "TryOhm sensor: %d\n" % self.id
        s += "Detection: %s\n" % self.read().name
        s += "----------"
        return s

    def __dict__(self):
        return {
            "name" : self.name,
            "id" : self.id,
            "detection": self.read()
        }

class TryOhmSensors(ComponentsHolder):

    def __init__(self, sensors):
        super().__init__('TryOhm sensors', sensors, TryOhm)

    def read_all_sensors(self):
        results = {}
        for sensor in self.components:
            results[sensor] = self.components[sensor].read()
        return results
