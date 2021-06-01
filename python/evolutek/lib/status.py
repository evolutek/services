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

    @staticmethod
    def get_status(dict):
        try:
            return RobotStatus(dict['status'])
        except:
            return RobotStatus.Unknow
