#!/bin/python3

from argparse import ArgumentParser
from cellaserv.proxy import CellaservProxy
from time import sleep

SPEED = 500
ACC = 500

robot = None
sensor = None
cs = None
dist = None

def adjust_gains(w1, w2, avg):

    cs.trajman[robot].recalibration(sens=0)
    sleep(3)

    measure1 = cs.actuators[robot].recal_sensor_read(id=sensor, repetitions=10)
    print("### MEASURE")
    print(f"Measure: {measure1}")

    cs.trajman[robot].move_trsl(dest=dist, acc=ACC, dec=ACC,
                                maxspeed=SPEED, sens=1)
    # ACC = DEC => T = D/S + S/ACC
    sleep(dist/SPEED + SPEED/ACC + 0.5)

    measure2 = cs.actuators[robot].recal_sensor_read(id=sensor, repetitions=10)
    print("### MEASURE")
    print(f"Measured: {measure2}")

    side = measure1 > measure2
    if sensor == 1: side = not side
    print(f"### {'Right' if side else 'Left'} drift")

    adjust = float(input("Scale of the adjustment: "))/1000
    if not side: adjust *= -1
    gain = w1/avg + adjust
    print(f"New gain: {gain}")

    cs.trajman[robot].move_trsl(dest=dist-30, acc=ACC, dec=ACC,
                                maxspeed=SPEED, sens=0)
    sleep(dist/SPEED + SPEED/ACC + 0.5)

    w1, w2 = avg*gain, avg*(2-gain)
    print(f"w1={w1} w2={w2}")

    cs.trajman[robot].set_wheels_diameter(w1=w1, w2=w2)
    return w1, w2


def parsing():

    global robot
    global sensor
    global dist

    parser = ArgumentParser(description='Configuration of the gains of the robot using recal sensors')
    parser.add_argument("robot", help="Robot to configure (pal or pmi)")
    parser.add_argument("sensor", help="Sensor to use (left or right)")
    parser.add_argument("-d", "--distance", help="The distance the robot will travel", default=1300)
    args = parser.parse_args()

    args.robot = args.robot.lower()
    if args.robot not in ['pal', 'pmi']:
        print('Unknown robot')
        print('Available robots: [pal, pmi]')
        return False
    robot = args.robot

    args.sensor = args.sensor.lower()
    if args.sensor not in ['left', 'right']:
        print('Unknown sensor')
        print('Available sensors: [left, right]')
        return False
    sensor = 1 if args.sensor == 'left' else 2

    dist = float(args.distance)
    return True


def main():

    if not parsing():
        return

    global cs
    cs = CellaservProxy()

    old = cs.trajman[robot].get_wheels()
    w1, w2 = old['left_diameter'], old['right_diameter']
    avg = (w1+w2)/2
    gain = w1/avg
    print(f"Current gain: {gain}")
    print(f"w1={w1} w2={w2}")

    print()
    side = 'left' if sensor == 1 else 'right'
    print(f"The robot will make a distance measurement on its {side}")
    print(f"Then it will move forward by {dist} and make a second measurement")
    print(f"At this point it know if it drifted left or right and will ask you a scale")
    print(f"Then it will adjust its gains with the scale you gave")
    print(f"Giving a negative scale will make the adjustment in the opposite direction")
    print(f"If you think the measurements are wrong, give a scale of 0")
    print(f"Hit CTRL+C to stop the operation and write the values")
    input("Ready ?")

    try:
        while True:
            w1, w2 = adjust_gains(w1, w2, avg)
    except KeyboardInterrupt:
        pass

    print(f"w1={w1} w2={w2}")
    res = input("Write ? (y/N)")
    if(res.lower() == 'y'):
        cs.config.set(section=robot, option='wheel_diam1', value=str(w1))
        cs.config.set(section=robot, option='wheel_diam2', value=str(w2))


if __name__ == "__main__":
    main()