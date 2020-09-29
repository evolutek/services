import adafruit_tca9548a
import adafruit_tcs34725
import board
import busio
import time

# RGB sensors class
# sensors: list of sensors to init
# sample_size: size of the sample for calibration
# Sensors models: TCS34725
# Sensors are multiplexed with a TCA9548A
class RGBSensors:

    def __init__(self, sensors, sample_size):

        print('[RGB_SENSORS] Init RGB Sensors')

        i2c = busio.I2C(board.SCL, board.SDA)
        self.tca = adafruit_tca9548a.TCA9548A(i2c)

        self.sensors = {}
        self.calibrations = {}

        for i in sensors:
            print('[RGB_SENSORS] Initializing RGB sensor %d' % i)
            if i < 1 or i > 8:
                print('[RGB_SENSORS] Bad RGB sensor number %d' % i)
                continue
            self.sensors[i] = adafruit_tcs34725.TCS34725(self.tca[i - 1])
            self.calibration(i, sample_size)

        print('[RGB_SENSORS] RGB Sensors initialized')

    def __str__(self):
        s = '---RGB Sensors:---\n'
        for key in self.sensors:
            s += 'sensor %d with calibration %s\n' % (key, self.calibrations[key])
        return s

    # Calibrate the sensor
    # i: number of the sensor
    # sample_size: size of the sample
    # Will read n frame an make a mean
    def calibration(self, i, sample_size):
        #print('[RGB_SENSORS] Calibrating RGB sensor %d' % i)
        if not i in self.sensors:
            print('[RGB_SENSORS] Bad RGB sensor number %d' % i)
            return None

        r, g, b = 0, 0, 0
        for n in range(sample_size):
            rgb = self.read_sensor(i, "calibration")
            print(rgb)
            r += int(rgb[0])
            g += int(rgb[1])
            b += int(rgb[2])
            time.sleep(0.1)

        self.calibrations[i] = (r // sample_size, g // sample_size, b // sample_size)

    # Return the difference between readed colors and the calibration
    # i: number of the sensor
    def get_diff_colors(self, i):
        if not i in self.sensors:
            print('[RGB_SENSORS] Bad RGB sensor number %d' % i)
            return None

        rgb = self.read_sensor(i, "calibration")
        cal = self.calibrations[i]
        return (rgb[0] - cal[0], rgb[1] - cal[1], rgb[2] - cal[2])


    # Read a sensor
    # i: number of the sensor
    def read_sensor(self, i, mode):
        if not i in self.sensors:
            print('[RGB_SENSORS] Bad RGB sensor number %d' % i)
            return None
        if (mode == "calibration"):
            return self.sensors[i].color_rgb_bytes
        result = self.sensors[i].color_rgb_bytes
        if (result[0] > result[1] and result[0] > result[2]):
            return str(result) + ": " + "red"
        elif (result[1] > result[0] and result[1] > result[2]):
            return str(result) +  ": " + "green"
        else:
            return str(result) + ": " + "unknown"
