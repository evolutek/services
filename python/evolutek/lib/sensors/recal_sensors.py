from evolutek.lib.component import Component, ComponentsHolder
import time

MIN_VOLTAGE = 0.6
MAX_VOLTAGE = 3.0
MIN_DISTANCE = 60
MAX_DISTANCE = 1530

CALIB_SLOPE1 = -0.00935088191857932
CALIB_INTERCEPT1 = -12.148812684023294
CALIB_SLOPE2 = 0.010548651997436593
CALIB_INTERCEPT2 = -18.715658876308545
CALIB_MIDPOINT = 330


def calibration(x):
    slope = CALIB_SLOPE1 if x < CALIB_MIDPOINT else CALIB_SLOPE2
    intercept = CALIB_INTERCEPT1 if x < CALIB_MIDPOINT else CALIB_INTERCEPT2
    err = slope * x + intercept
    return x - err


def interp(a, b, alpha):
    return (b - a) * alpha + a


def clamp(x, low, high):
    return max(low, min(x, high))


class RecalSensor(Component):
    def __init__(self, id, adc):
        self.adc = adc
        super().__init__("RecalSensor", id)

    def read(self, repetitions=1, use_calibration=True):
        res = 0
        for i in range(repetitions):
            raw = self.adc.read()
            voltage = clamp(raw, MIN_VOLTAGE, MAX_VOLTAGE)
            alpha = (voltage - MIN_VOLTAGE) / (MAX_VOLTAGE - MIN_VOLTAGE)
            res += interp(MIN_DISTANCE, MAX_DISTANCE, alpha)
            if i < repetitions-1: time.sleep(0.1)
        res /= repetitions
        return calibration(res) if use_calibration else res

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

    def read_all_sensors(self):
        results = {}
        for sensor in self.components:
            results[sensor] = self.components[sensor].read()
        return results
