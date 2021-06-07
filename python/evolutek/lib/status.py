from enum import Enum

class RobotStatus(Enum):
    # Common
    Aborted = 'aborted'
    Disabled = 'disabled'
    Done = 'done'
    Failed = 'failed'
    NotStarted = 'not-started'
    Ok = 'ok'
    Unknow = 'unknow'

    # Move
    HasAvoid = 'has-avoid'
    NotReached = 'not-reached'
    Reached = 'reached'
    Unreachable = 'unreachable'

    @staticmethod
    def get_status(dict):
        try:
            return RobotStatus(dict['status'])
        except:
            return RobotStatus.Unknow
