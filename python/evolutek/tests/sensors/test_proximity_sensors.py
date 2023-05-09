from evolutek.lib.sensors.proximity_sensors import ProximitySensors
from evolutek.lib.gpio.gpio_factory import GpioType, create_gpio

from time import sleep

sensors = {
    1 : [create_gpio(0, 'sensor1', dir=False, type=GpioType.MCP)],
    2 : [create_gpio(1, 'sensor2', dir=False, type=GpioType.MCP)]
}

proximity_sensors = ProximitySensors(sensors)
print(proximity_sensors)

while True:
    for sensor in proximity_sensors:
        print(proximity_sensors[sensor])
    sleep(1)
