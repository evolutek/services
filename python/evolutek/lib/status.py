from enum import Enum

class RobotStatus(Enum):
    # Common
    Aborted = 'aborted'
    Disabled = 'disabled'
    Done = 'done'
    Failed = 'failed'
    NotStarted = 'not-started'
    Ok = 'ok'
    Timeout = 'timeout'
    Unknown = 'unknown'

    # Move
    HasAvoid = 'has-avoid'
    NotReached = 'not-reached'
    Reached = 'reached'
    Unreachable = 'unreachable'

    @staticmethod
    def get_status(dict):
        if isinstance(dict, str):
            dict = { 'status' : dict }
        try:
            return RobotStatus(dict['status'])
        except:
            return RobotStatus.Unknown

    @staticmethod
    def return_status(status, **kwargs):
        kwargs['status'] = status.value
        return kwargs

    @staticmethod
    def check(*args, score=0):
        for stat in args:
            stat = RobotStatus.get_status(stat)
            if stat != RobotStatus.Done and stat != RobotStatus.Reached:
                return RobotStatus.return_status(RobotStatus.Failed)
        return RobotStatus.return_status(RobotStatus.Done, score=score)
