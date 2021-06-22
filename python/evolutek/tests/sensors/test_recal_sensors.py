from time import sleep

from cellaserv.service import ConfigVariable
from evolutek.lib.gpio.gpio_factory import create_adc, AdcType
from evolutek.lib.sensors.recal_sensors import RecalSensors

ROBOT='pal'

left_slope1 = ConfigVariable(section=ROBOT, option="left_slope1", coerc=float)
left_intercept1 = ConfigVariable(section=ROBOT, option="left_intercept1", coerc=float)
left_slope2 = ConfigVariable(section=ROBOT, option="left_slope2", coerc=float)
left_intercept2 = ConfigVariable(section=ROBOT, option="left_intercept2", coerc=float)
right_slope1 = ConfigVariable(section=ROBOT, option="right_slope1", coerc=float)
right_intercept1 = ConfigVariable(section=ROBOT, option="right_intercept1", coerc=float)
right_slope2 = ConfigVariable(section=ROBOT, option="right_slope2", coerc=float)
right_intercept2 = ConfigVariable(section=ROBOT, option="right_intercept2", coerc=float)
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
