from enum import Enum
from math import sqrt

class RGBColor:

    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

    @staticmethod
    def from_tupple(t):
        return RGBColor(r, g, b)

    def to_tupple(self):
        return (self.r, self.g, self.b)

    def __str__(self) -> str:
        return  f"(R, G, B): ({self.r}, {self.g}, {self.b})"

    def __eq__(self, color) -> bool:
        return (
            self.r == color.r and
            self.g == color.g and
            self.b == color.b
        )

    def __add__(self, color):
        return RGBColor(
            self.r + color.r,
            self.g + color.g,
            self.b + color.b
        )

    def __sub__(self, color):
        return RGBColor(
            self.r - color.r,
            self.g - color.g,
            self.b - color.b
        )

    def __div__(self, div: int):
        return RGBColor(
            self.r / div,
            self.g / div,
            self.b / div
        )

    def __mul__(self, coef: float):
        if coef < 0.0 or coef > 1.0:
            return Color.Black.value

        return RGBColor(self.r * coef, self.g * coef, self.b * coef)

    @staticmethod
    def mean(colors):
        result = RGBColor(0, 0, 0)
        for color in colors:
            result += color
        return result / len(colors)
    
    def compute_dist(self, color):
        tmp = self.__sub__(color)
        return sqrt(
            tmp.r ** 2 + tmp.g **2 + tmp.b **2
        )

class Color(Enum):
    Black =     RGBColor(0, 0, 0)
    Blue =      RGBColor(0, 0, 255)
    Brown =     RGBColor(76, 43, 32)
    Green =     RGBColor(0, 255, 0)
    Orange =    RGBColor(255, 50, 0)
    Pink =      RGBColor(188, 64, 119)
    Purple =    RGBColor(115, 25, 115)
    Red =       RGBColor(255, 0, 0)
    Yellow =    RGBColor(247, 181, 0)
    Unknown =   RGBColor(-1, -1, -1)

    @staticmethod
    def get_by_name(name):
        try:
            return Color.__members__[name.capitalize()]
        except:
            return Color.Unknown
        
    @staticmethod
    def get_by_rgb(rgb_color):
        for color in Color.__members__:
            if rgb_color == color.value:
                return color
        return Color.Unknown
    
    @staticmethod
    def get_closest_color(rgb_color, colors):
        closest = Color.Unknow
        min_dist = rgb_color.compute_dist(Color.Unknow.value)
        for color in colors:
            dist = rgb_color.compute_dist(color.value)
            if dist < min_dist:
                min_dist = dist
                closest = color
        return closest
