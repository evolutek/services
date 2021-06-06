from evolutek.lib.component import Component, ComponentsHolder

MIN_VOLTAGE = 0.6
MAX_VOLTAGE = 3.0
MIN_DISTANCE = 50
MAX_DISTANCE = 1500

def interp(a, b, alpha):
    return (b - a) * alpha + a


def clamp(x, low, high):
    return max(low, min(x, high))


class RecalSensor(Component):
    def __init__(self, id, adc):
        self.adc = adc
        super().__init__("RecalSensor", id)

    def read(self):
        raw = self.adc.read()
        voltage = clamp(raw, MIN_VOLTAGE, MAX_VOLTAGE)
        alpha = (voltage - MIN_VOLTAGE) / (MAX_VOLTAGE - MIN_VOLTAGE)
        return interp(MIN_DISTANCE, MAX_DISTANCE, alpha)

    def __dict__(self):
        return {
            "name" : self.name,
            "id": self.id,
            "distance": self.read()
        }



class RecalSensors(ComponentsHolder):

    def __init__(self, adcs):
        super().__init__("Recal sensors", adcs, RecalSensor)

    def read_all_sensors(self):
        return map(lambda sensor: self.components[sensor].read(), self)
