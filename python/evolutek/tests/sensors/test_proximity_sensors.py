from evolutek.lib.sensors.proximity_sensors import ProximitySensors
from evolutek.lib.gpio.gpio_factory import GpioType, create_gpio

from time import sleep

sensors = {
    8 : [create_gpio(8, 'sensor1', dir=False, type=GpioType.MCP)],
    9 : [create_gpio(9, 'sensor2', dir=False, type=GpioType.MCP)],
    10 : [create_gpio(10, 'sensor3', dir=False, type=GpioType.MCP)],
    11 : [create_gpio(11, 'sensor4', dir=False, type=GpioType.MCP)],
    12 : [create_gpio(12, 'sensor5', dir=False, type=GpioType.MCP)],
    13 : [create_gpio(13, 'sensor6', dir=False, type=GpioType.MCP)],

    23 : [create_gpio(23, 'sensor7', dir=False, type=GpioType.MCP)],
    24 : [create_gpio(24, 'sensor8', dir=False, type=GpioType.MCP)],
    25 : [create_gpio(25, 'sensor9', dir=False, type=GpioType.MCP)],
    26 : [create_gpio(26, 'sensor10', dir=False, type=GpioType.MCP)],
    27 : [create_gpio(27, 'sensor11', dir=False, type=GpioType.MCP)],
    28 : [create_gpio(28, 'sensor12', dir=False, type=GpioType.MCP)]
}

proximity_sensors = ProximitySensors(sensors)
print(proximity_sensors)

while True:
    for sensor in proximity_sensors:
        print(proximity_sensors[sensor])
    sleep(1)

