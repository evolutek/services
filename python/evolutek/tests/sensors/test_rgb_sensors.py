from time import sleep

from evolutek.lib.sensors.rgb_sensors import RGBSensors

rgb_sensors = RGBSensors([1])
print(rgb_sensors)

for sensor in rgb_sensors:
    rgb_sensors[sensor].calibrate()

while True:
    for sensor in rgb_sensors:
        print('Sensor %s Color: (%s)' % (sensor, rgb_sensors[sensor].read().value))
    print("\n---------------------------------------\n")
    sleep(1)
