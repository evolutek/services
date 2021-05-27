from enum import Enum

class RobotStatus(Enum):
    # Common
    Done = 'done'
    Failed = 'Failed'
    Unknow = 'unknow'

    # Move
    Reached = 'reached'
    NotReached = 'not-reached'
    HasAvoid = 'has-avoid'
    Unreachable = 'unreachable'
