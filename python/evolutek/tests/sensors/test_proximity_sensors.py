from evolutek.lib.sensors.proximity_sensors import ProximitySensors
from evolutek.lib.gpio.gpio_factory import GpioType, create_gpio

from time import sleep

sensors = {
    1 : [create_gpio(24, 'sensor1', dir=False, type=GpioType.MCP)],
    2 : [create_gpio(25, 'sensor2', dir=False, type=GpioType.MCP)],
    3 : [create_gpio(26, 'sensor3', dir=False, type=GpioType.MCP)],
    4 : [create_gpio(27, 'sensor4', dir=False, type=GpioType.MCP)]
}

proximity_sensors = ProximitySensors(sensors)
print(proximity_sensors)

while True:
    for sensor in proximity_sensors:
        print(proximity_sensors[sensor])
    sleep(1)
