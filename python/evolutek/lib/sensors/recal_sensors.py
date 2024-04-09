from evolutek.lib.component import Component, ComponentsHolder
import time

MIN_VOLTAGE = 0.6
MAX_VOLTAGE = 3.0
MIN_DISTANCE = 100
MAX_DISTANCE = 1250

class RecalSensor(Component):
    def __init__(self, id, adc):
        self.adc = adc
        self.points: list[tuple[float, float]] = []
        super().__init__("RecalSensor", id)

    def calibrate(self, points: list[list[float]]):
        self.points = [(p[0], p[1]) for p in points]

    def read(self, repetitions=1, raw=False):
        use_calibration = (not raw) and (len(self.points) >= 2)

        res = 0
        for i in range(repetitions):
            raw = self.adc.read()
            voltage = max(MIN_VOLTAGE, min(raw, MAX_VOLTAGE))
            alpha = (voltage - MIN_VOLTAGE) / (MAX_VOLTAGE - MIN_VOLTAGE)
            res += (MAX_DISTANCE - MIN_DISTANCE) * alpha + MIN_DISTANCE
            if i < repetitions - 1: time.sleep(0.05)
        res /= repetitions

        if use_calibration:
            if res < self.points[0][0]:
                x1, y1 = self.points[0]
                x2, y2 = self.points[1]
            elif res > self.points[-1][0]:
                x1, y1 = self.points[-2]
                x2, y2 = self.points[-1]
            else:
                for i in range(len(self.points) - 1):
                    x1, y1 = self.points[i]
                    x2, y2 = self.points[i + 1]
                    if res >= x1 and res <= x2:
                        break
            res = ((res - x1) / (x2 - x1)) * (y2 - y1) + y1
        else:
            print("Calibration unused")

        return res

    def __str__(self):
        s = "----------\n"
        s += "Recal sensor: %d\n" % self.id
        s += "Distance: %d\n" % self.read()
        s += "----------"
        return s

    def __dict__(self):
        return {
            "name" : self.name,
            "id": self.id,
            "distance": self.read()
        }


class RecalSensors(ComponentsHolder):

    def __init__(self, adcs):
        super().__init__("Recal sensors", adcs, RecalSensor)

    def read_all_sensors(self, **kwargs):
        results = {}
        for sensor in self.components:
            results[sensor] = self.components[sensor].read(kwargs)
        return results
