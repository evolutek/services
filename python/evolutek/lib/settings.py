#!/usr/bin/env python3

#TODO: find a solution to know witch robot to launch in simulation

import socket

__doc__ = """Add evolutek's specific configuration to cellaserv.settings."""

from cellaserv.proxy import CellaservProxy
from cellaserv.settings import make_setting

hostname = socket.gethostname()

if hostname not in ['pal', 'pmi']:
    make_setting('SIMULATION', True, 'evolutek', 'simulation', 'SIMULATION')
    cs = CellaservProxy()
    robot = None
    try:
        robot = cs.config.get(section='simulation', option='robot')
    except:
        pass
    make_setting('ROBOT', robot, 'evolutek', 'robot', 'ROBOT')
else:
    make_setting('SIMULATION', False, 'evolutek', 'simulation', 'SIMULATION')
    make_setting('ROBOT', hostname, 'evolutek', 'robot', 'ROBOT')

from cellaserv.settings import make_logger
from cellaserv.settings import ROBOT
from cellaserv.settings import SIMULATION

SIMULATION = bool(SIMULATION)

logger = make_logger(__name__)
logger.debug('ROBOT: %s', ROBOT)
logger.debug('SIMULATION: %s', SIMULATION)
