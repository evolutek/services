#!/usr/bin/env python3

import configparser
import os

config = configparser.ConfigParser()
config.read(['/etc/conf.d/evolutek'])

ROBOT = "pal"
try:
    ROBOT = config.get("evolutek", "robot")
except:
    pass
ROBOT = os.environ.get("EVO_ROBOT", ROBOT)

USE_CONFIG = False
try:
    USE_CONFIG = bool(config.get("evolutek", "use_config"))
except:
    pass
USE_CONFIG = bool(os.environ.get("EVO_USE_CONFIG", USE_CONFIG))


def main():
    print("ROBOT: " + ROBOT)
    print("USE_CONFIG: " + str(USE_CONFIG))

if __name__ == "__main__":
    main()
