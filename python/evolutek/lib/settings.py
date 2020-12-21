#!/usr/bin/env python3

# Hold the settings of the code

import socket

__doc__ = """Add evolutek's specific configuration to cellaserv.settings."""

from cellaserv.proxy import CellaservProxy
from cellaserv.settings import make_setting

# Get the hostname of the machine
hostname = socket.gethostname()

# Check if the machine is not on a Rpi (Robot, Beacon)
if hostname not in ["pal", "pmi", "beacon"]:

    # Set the simulation flag
    make_setting("SIMULATION", True, "evolutek", "simulation", "SIMULATION")
    cs = CellaservProxy()
    robot = None

    # Set the robot name if one is setted for the simulation
    try:
        robot = cs.config.get(section="simulation", option="robot")
        make_setting("ROBOT", robot, "evolutek", "robot", "ROBOT")

    # Set robot to None
    except:
        make_setting("ROBOT", "None", "evolutek", "robot", "ROBOT")
        pass

# Unset simulation flag and set robot name
else:
    make_setting("SIMULATION", False, "evolutek", "simulation", "SIMULATION")
    make_setting("ROBOT", hostname, "evolutek", "robot", "ROBOT")

# Imported part by the code
from cellaserv.settings import ROBOT, SIMULATION, make_logger

SIMULATION = SIMULATION == "True"

# Log robot name and simulation flag
logger = make_logger(__name__)
logger.debug("ROBOT: %s", ROBOT)
logger.debug("SIMULATION: %s", SIMULATION)
