from enum import Enum

class Color(Enum):
    Black = (0, 0, 0)
    Blue = (0, 0, 255)
    Green = (0, 255, 0)
    Orange = (255, 50, 0)
    Red = (255, 0, 0)
    Yellow = (255, 255, 0)
    Unknown = (-1, -1, -1)

    @staticmethod
    def get_by_name(name):
        try:
            return Color.__members__[name.capitalize()]
        except:
            return Color.Unknown
