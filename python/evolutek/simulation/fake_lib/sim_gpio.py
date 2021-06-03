from enum import Enum
from threading import Thread
from time import sleep

from evolutek.lib.component import Component

class Edge(Enum):
    RISING = 0
    FALLING = 1
    BOTH = 2

class Gpio(Component):
    def __init__(self, id, name, dir=True, event=None, edge=Edge.BOTH, default_value=False):
        super().__init__("GPIO", id)
        