import time
import board
import busio
import adafruit_tca9548a
import adafruit_tcs34725

def print_sensor(sensor):
    temp = sensor.color_temperature
    lux = sensor.lux

    print('Color: ({0}, {1}, {2})'.format(*sensor.color_rgb_bytes))

    print("t: %s, l: %s" % (str(temp), str(lux)))


# Create I2C bus as normal
i2c = busio.I2C(board.SCL, board.SDA)

# Create the TCA9548A object and give it the I2C bus
tca = adafruit_tca9548a.TCA9548A(i2c)

sensor1 = adafruit_tcs34725.TCS34725(tca[1])
sensor2 = adafruit_tcs34725.TCS34725(tca[2])



while True:
    print('Sensor1 :')
    print_sensor(sensor1)
    print('Sensor2 :')
    print_sensor(sensor2)
    time.sleep(1)
