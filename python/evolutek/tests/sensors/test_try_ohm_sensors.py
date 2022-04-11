from evolutek.lib.sensors.try_ohm_sensors import TryOhmSensors
from evolutek.lib.gpio.gpio_factory import GpioType, create_gpio

from time import sleep

sensors = {
    1 : [
        create_gpio(13, 'sensor1a', dir=False, type=GpioType.RPI),
        create_gpio(19, 'sensor1b', dir=False, type=GpioType.RPI)
    ],
    2 : [
        create_gpio(16, 'sensor2a', dir=False, type=GpioType.RPI),
        create_gpio(26, 'sensor2b', dir=False, type=GpioType.RPI)
    ]
}

try_ohm_sensors = TryOhmSensors(sensors)
print(try_ohm_sensors)

while True:
    for sensor in try_ohm_sensors:
        print(try_ohm_sensors[sensor])
    sleep(1)
