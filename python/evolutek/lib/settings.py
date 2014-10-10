#!/usr/bin/env python3

__doc__ = """Add evolutek's specific configuration to cellaserv.settings."""

from cellaserv.settings import make_setting

make_setting('ROBOT', 'pal', 'evolutek', 'robot', 'ROBOT')

from cellaserv.settings import make_logger
from cellaserv.settings import ROBOT

logger = make_logger(__name__)
logger.debug('ROBOT: %s', ROBOT)
