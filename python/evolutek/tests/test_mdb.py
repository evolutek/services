from evolutek.lib.mdb import Mdb

from time import sleep

class Test_Mdb():

    def __init__(self):

        mdb = Mdb(16, debug=True)

        while True:
            scan = mdb.get_scan()
            print("---- New scan -----")
            for i in range(len(scan)):
                print("%d: %f" % (i + 1, scan[i]))
            sleep(1)

def main():
    Test_Mdb()

if __name__ == "__main__":
    main()
