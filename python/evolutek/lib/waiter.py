from time import sleep
import os

def waitConfig(cs):
    Offline = True
    while Offline:
        try:
            info = cs.config.get_section('tim')
            Offline = False
        except:
            print("waiting for config")
            sleep(1)

def waitBeacon():
    hostname = "pi"
    while True:
        r = os.system("ping -c 1 " + hostname)
        if r == 0:
            return
        sleep(1)

