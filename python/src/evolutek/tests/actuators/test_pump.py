from evolutek.lib.actuators.pump import PumpController
from evolutek.lib.gpio.gpio_factory import GpioType, create_gpio

from time import sleep

pumps = {
    1: [
        create_gpio(0, 'pump1', dir=True, type=GpioType.MCP),
        create_gpio(1, 'ev1', dir=True, type=GpioType.MCP)
    ],
    2 : [
        create_gpio(2, 'pump2', dir=True, type=GpioType.MCP),
        create_gpio(3, 'ev2', dir=True, type=GpioType.MCP)
    ],
    3 : [
        create_gpio(4, 'pump3', dir=True, type=GpioType.MCP),
        create_gpio(5, 'ev3', dir=True, type=GpioType.MCP)
    ],
    4: [
        create_gpio(6, 'pump4', dir=True, type=GpioType.MCP),
        create_gpio(7, 'ev4', dir=True, type=GpioType.MCP)
    ]
}


pump_controller = PumpController(pumps, 1)
print(pump_controller)

for pump in pump_controller:
    pump_controller[pump].get()
    sleep(5)

pump_controller.drops([1,2,3,4])
