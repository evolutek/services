from time import sleep

import adafruit_tca9548a
import adafruit_tcs34725
import board
import busio

#rgb_sensors = RGBSensors([3])
#print(rgb_sensors)

TCA = adafruit_tca9548a.TCA9548A(busio.I2C(board.SCL, board.SDA))
sensor = adafruit_tcs34725.TCS34725(TCA[1])

sensor.integration_time = 160
sensor.gain = 60

#for sensor in rgb_sensors:
#    rgb_sensors[sensor].calibrate()

while True:
    r,g,b = sensor.color_rgb_bytes
    #r,g,b = pow(r, 1/2.5), pow(g, 1/2.5), pow(b, 1/2.5)

    print(r / 28,g / 14,b / 6)


    #for sensor in rgb_sensors:
    #    print('Sensor %s Color: (%s)' % (sensor, rgb_sensors[sensor].read().value))
    
    sleep(0.3)