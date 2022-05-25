from enum import Enum
from math import sqrt

class RGBColor:

    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

    @staticmethod
    def from_tupple(t):
        return RGBColor(t[0], t[1], t[2])

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

    def get_rgb_percentages(self):
        sum = self.r + self.g + self.b
        if sum == 0:
            return (0, 0, 0)
        return (self.r / sum, self.g / sum, self.b / sum)

    @staticmethod
    def mean(colors):
        result = RGBColor(0, 0, 0)
        for color in colors:
            result += color
        return result.__div__(len(colors))

    @staticmethod
    def compute_dist(a, b):
        percentages_a = a.get_rgb_percentages()
        percentages_b = b.get_rgb_percentages()

        return ((
            abs(percentages_a[0] - percentages_b[0]) +
            abs(percentages_a[1] - percentages_b[1]) +
            abs(percentages_a[2] - percentages_b[2])
        ) / 3)

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
        for color in Color.__members__.values():
            if rgb_color == color.value:
                return color
        return Color.Unknown
    
    @staticmethod
    def get_closest_color(rgb_color, colors):
        closest = None
        min_dist = None
        for color in colors:
            dist = RGBColor.compute_dist(rgb_color, color.value)
            if min_dist is None or dist < min_dist:
                min_dist = dist
                closest = color
        return closest

