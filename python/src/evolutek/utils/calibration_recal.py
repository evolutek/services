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
#DIST_SIDE = 15

# The minimum measurable distance for the sensor is 100mm
DIST_MIN = 100
# The maximum measurable distance for the sensor is 2500mm
DIST_MAX = 1165

DISTS = [100, 200, 500, 750, 1000]


def wait():
    input("Press enter to continue\n")


def obstacle(dist):
    print(f"Place an obstacle {dist} mm in front of the sensor")
    #print(f"{dist - DIST_SIDE} from the side of the robot")


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
    button = "the nearest from the wheels" if sensorid == 1 else "the farest from the wheels"
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

    points = []
    str_points = []

    for dist in DISTS:
        obstacle(dist)
        wait()
        measure = sensor.read(repetitions = 10, raw = True)
        print(f"Measured {measure}")
        str_points.append(f"[{measure:.1f}, {dist}]")
        points.append([measure, dist])

    print("Points: [" + ", ".join(str_points) + "]")
    sensor.calibrate(points)

    try:
        while True:
            print(f"Measurement: {sensor.read(repetitions = 10)}")
            sleep(0.1)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
