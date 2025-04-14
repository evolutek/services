from time import sleep

from cellaserv.proxy import CellaservProxy
from evolutek.lib.gpio.gpio_factory import create_adc, AdcType
from evolutek.lib.sensors.recal_sensors import RecalSensors

from evolutek.lib.settings import ROBOT

cs = CellaservProxy()
left_slope1 = float(cs.config.get(ROBOT, "left_slope1"))
left_intercept1 = float(cs.config.get(ROBOT, "left_intercept1"))
left_slope2 = float(cs.config.get(ROBOT, "left_slope2"))
left_intercept2 = float(cs.config.get(ROBOT, "left_intercept2"))
right_slope1 = float(cs.config.get(ROBOT, "right_slope1"))
right_intercept1 = float(cs.config.get(ROBOT, "right_intercept1"))
right_slope2 = float(cs.config.get(ROBOT, "right_slope2"))
right_intercept2 = float(cs.config.get(ROBOT, "right_intercept2"))

sensors = RecalSensors(
    {
        1: [create_adc(0, "recal1", type=AdcType.ADS)],
        2: [create_adc(1, "recal2", type=AdcType.ADS)]
    }
)
sensors[1].calibrate(left_slope1, left_intercept1, left_slope2, left_intercept2)
sensors[2].calibrate(right_slope1, right_intercept1, right_slope2, right_intercept2)

print(sensors.is_initialized())

while True:
    for sensor in sensors:
        print(f"Recal1: {sensors[1].read(repetitions=10)}, Recal2: {sensors[2].read(repetitions=10)}")
