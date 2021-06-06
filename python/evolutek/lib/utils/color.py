from enum import Enum

class Color(Enum):
    Black = (0, 0, 0)
    Blue = (0, 0, 255)
    Green = (0, 255, 0)
    Orange = (255, 10, 0)
    Red = (255, 0, 0)
    Yellow = (255, 255, 0)
    Unknow = (-1, -1, -1)

    @staticmethod
    def get_by_name(self, name):
        try:
            return Color.__members__[name]
        except:
            return Color.Unknow
