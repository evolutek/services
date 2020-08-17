from evolutek.lib.mdb import Mdb
from evolutek.lib.gpio import Gpio
import board

from time import sleep

class Test_Mdb():

    def __init__(self):

        mdb = Mdb(16, debug=True, leds_gpio=board.D12,
                front_sensors=[15,16,1,2,3],
                left_sensors=[11,12,13,14,15],
                back_sensors=[7,8,9,10,11],
                right_sensors=[3,4,5,6,7])

        while True:
            scan = mdb.get_scan()
            print("---- New scan -----")
            for i in range(len(scan)):
                print("%d: %f" % (i + 1, scan[i]))
            sleep(1)
            print("---- Obstacles ----")
            print("Front: " + str(mdb.get_front()))
            print("Back: " + str(mdb.get_back()))
            print("Right: " + str(mdb.get_right()))
            print("Left: " + str(mdb.get_left()))
            print("Is robot: " + str(mdb.get_is_robot()))


def main():
    Test_Mdb()

if __name__ == "__main__":
    main()
