from enum import Enum
from evolutek.lib.gpio.gpio import Edge

from evolutek.lib.settings import SIMULATION

if SIMULATION:
    import evolutek.lib.gpio.fake_gpio as fake_gpio
else:
    import evolutek.lib.gpio.ads1115_adc as ads1115_adc
    import evolutek.lib.gpio.rpi_gpio as rpi_gpio
    import evolutek.lib.gpio.mcp23017_gpio as mcp23017_gpio

# Gpio type
class GpioType(Enum):
    Default = 0
    RPI = 1
    MCP = 2

# Pwm type
class PwmType(Enum):
    Default = 0
    RPI = 1

# Adc type
class AdcType(Enum):
    Default = 0
    ADS = 1

# Create a Gpio object according to the desired type
def create_gpio(id, name, dir=True, event=None, edge=Edge.BOTH, default_value=False, type=GpioType.Default):
    # If the code is running in simulation, create a fake pwm
    if SIMULATION:
        return fake_gpio.Gpio(id, name, dir, event, edge, default_value)

    if type == GpioType.MCP:

        if not mcp23017_gpio.wasInitialized():
            mcp23017_gpio.initialize()

        return mcp23017_gpio.Gpio(id, name, dir, event, edge, default_value)

    if type == GpioType.Default or type == GpioType.RPI:

        if not rpi_gpio.wasInitialized():
            rpi_gpio.initialize()

        return rpi_gpio.Gpio(id, name, dir, event, edge, default_value)

# Create a Pwm object according to the desired type
def create_pwm(id, name, dc=0, freq=0, type=PwmType.Default):
    # If the code is running in simulation, create a fake pwm
    if SIMULATION:
        return fake_gpio.Pwm(id, name, dir, dc, freq)

    if type == PwmType.Default or type == PwmType.RPI:

        if not rpi_gpio.wasInitialized():
            rpi_gpio.initialize()

        return rpi_gpio.Pwm(id, name, dir, dc, freq)

# Create a Adc object according to the desired type
def create_adc(id, name, type=AdcType.Default):
    # If the code is running in simulation, create a fake adc
    if SIMULATION:
        return fake_gpio.Adc(id, name)

    if type == AdcType.Default or type == AdcType.ADS:

        if not ads1115_adc.wasInitialized():
            ads1115_adc.initialize()

        return ads1115_adc.Adc(id, name)
