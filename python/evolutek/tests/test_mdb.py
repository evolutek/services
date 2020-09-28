from evolutek.lib.mdb import Mdb
from evolutek.lib.gpio import Gpio
import board

from time import sleep

class Test_Mdb():

    def __init__(self):

        mdb = Mdb()
        mdb.enable(0)

        while True:
            scan = mdb.get_scan()
            print("---- New scan -----")
            for i in range(len(scan)):
                print("%d: " % (i+1), end='')
                if scan[i] == 65535: print("ERROR")
                else: print("%2.f cm" % (scan[i] / 10))
            print("---- Obstacles ----")
            print("Front: " + str(mdb.get_front()))
            print("Back: " + str(mdb.get_back()))
            print("Is robot: " + str(mdb.get_is_robot()))
            sleep(0.1)


def main():
    Test_Mdb()

if __name__ == "__main__":
    main()
