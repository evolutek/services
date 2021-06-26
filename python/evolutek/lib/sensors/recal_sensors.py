from evolutek.lib.component import Component, ComponentsHolder
import time

MIN_VOLTAGE = 0.6
MAX_VOLTAGE = 3.0
MIN_DISTANCE = 60
MAX_DISTANCE = 1530
CALIB_MIDPOINT = 230

class RecalSensor(Component):

    def __init__(self, id, adc):
        self.adc = adc
        self.slope1 = 0
        self.slope2 = 0
        self.intercept1 = 0
        self.intercept2 = 0
        super().__init__("RecalSensor", id)

    def calibrate(self, slope1, intercept1, slope2, intercept2):
        self.slope1 = slope1
        self.intercept1 = intercept1
        self.slope2 = slope2
        self.intercept2 = intercept2

    def calibration(self, x):
        slope = self.slope1 if x < CALIB_MIDPOINT else self.slope2
        intercept = self.intercept1 if x < CALIB_MIDPOINT else self.intercept2
        err = slope * x + intercept
        return x - err

    def read(self, repetitions=1, use_calibration=True):
        res = 0
        for i in range(repetitions):
            raw = self.adc.read()
            voltage = max(MIN_VOLTAGE, min(raw, MAX_VOLTAGE))
            alpha = (voltage - MIN_VOLTAGE) / (MAX_VOLTAGE - MIN_VOLTAGE)
            res += (MAX_DISTANCE - MIN_DISTANCE) * alpha + MIN_DISTANCE
            if i < repetitions-1: time.sleep(0.05)
        res /= repetitions
        return self.calibration(res) if use_calibration else res

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
