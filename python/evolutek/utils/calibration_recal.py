#!/bin/python3

from evolutek.lib.gpio.gpio_factory import create_adc, AdcType
from evolutek.lib.sensors.recal_sensors import RecalSensor
from time import sleep

"""
 WARNING

 If you change these values, make sure you dont break the readings
 by checking the values in lib/sensors/recal_sensors.py

"""

# Distance between the glass of the sensor and the side of the robot
DIST_SIDE = 15

# The minimum measurable distance for the sensor is 100mm
DIST_MIN = 85 + DIST_SIDE
# The maximum measurable distance for the sensor is 2500mm
DIST_MAX = 1150 + DIST_SIDE

DIST_1 = 100 + DIST_SIDE
DIST_2 = 500 + DIST_SIDE
DIST_3 = 1100 + DIST_SIDE
def wait():
    input("Press enter to continue\n")

def obstacle(dist):
    print(f"Place an obstacle {dist}mm in front of the sensor")
    print(f"{dist - DIST_SIDE} from the side of the robot")

def main():

    print("Which sensor are you calibrating ?")
    print("Look at the robot from the back and enter L for left or R for right")
    raw = input().lower()
    if not raw or raw not in "rl":
        print("You must enter R or L")
        return
    sensorid = 1 if raw == "l" else 2

    obstacle(DIST_MIN)
    wait()
    button = "bottom" if sensorid == 1 else "top"
    print(f"Press the QA button ({button}) on the sensor for 1 second")
    print("The yellow LED led should start blinking")
    wait()
    obstacle(DIST_MAX)
    wait()
    print(f"Press the QA button ({button}) on the sensor for 1 second")
    print("The yellow LED led should stop blinking")
    wait()

    sensor = RecalSensor(sensorid, create_adc(
        sensorid-1,
        f"Recal{sensorid}",
        type=AdcType.ADS
    ))

    obstacle(DIST_1)
    wait()
    measure1 = sensor.read(repetitions=10, use_calibration=False)
    print(f"Measured {measure1}")
    obstacle(DIST_2)
    wait()
    measure2 = sensor.read(repetitions=10, use_calibration=False)
    print(f"Measured {measure2}")
    obstacle(DIST_3)
    wait()
    measure3 = sensor.read(repetitions=10, use_calibration=False)
    print(f"Measured {measure3}")
    err1 = measure1 - DIST_1
    err2 = measure2 - DIST_2
    err3 = measure3 - DIST_3

    slope1 = (err2 - err1) / (DIST_2 - DIST_1)
    intercept1 = err2 - (DIST_2)*slope1
    slope2 = (err3 - err2) / (DIST_3 - DIST_2)
    intercept2 = err2 - (DIST_2)*slope2

    side = "left" if sensorid == 1 else "right"
    print(f"{side}_slope1 = {slope1}")
    print(f"{side}_intercept1 = {intercept1}")
    print(f"{side}_slope2 = {slope2}")
    print(f"{side}_intercept2 = {intercept2}")

    sensor.calibrate(slope1, intercept1, slope2, intercept2)
    while True:
        print(f"Measurement: {sensor.read(repetitions=10)}")
        sleep(0.5)


if __name__ == "__main__":
    main()
