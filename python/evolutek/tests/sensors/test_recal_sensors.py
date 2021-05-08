from time import sleep

from evolutek.lib.gpio.gpio_factory import create_adc, AdcType
from evolutek.lib.sensors.recal_sensors import RecalSensors

sensors = RecalSensors({
    1: [create_adc(0, "Recal1", type=AdcType.ADS)], 
    2: [create_adc(1, "Recal2", type=AdcType.ADS)], 
})
print(sensors.is_initialized())
#print(sensors)

while True:
    for sensor in sensors:
        print(f"Recal1: {sensors[1].read()}, Recal2: {sensors[2].read()}")
        sleep(0.2)
