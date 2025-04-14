from enum import Enum
from threading import Thread
from time import sleep


# Types of edge for gpio
class Edge(Enum):
    BOTH = 2
    FALLING = 0
    RISING = 1


# Parent class IO
# id: id of the io
# name: name of io
# dir: True if output else False
# event: name of the event
class Io():

    def __init__(self, id, name, dir=True, event=None):
        self.id = id
        self.name = name
        self.dir = dir
        self.event = event
        self.value = None

    def __eq__(self, ident):
        return (ident[0] is not None and self.id == int(ident[0])) or self.name == ident[1]

    def __str__(self):
        return "id: %d\nname: %s\ndir: %s\nevent: %s\n"\
            % (self.id, self.name, str(self.dir), self.event)

    def __dict__(self):
        return {
            'id': self.id,
            'name': self.name,
            'dir': self.dir,
            'event': self.event,
        }


# PWM class
# Inherit of IO class
# dc: initial Duty Cycle
# freq: Freq of the PWM
class Pwm(Io):

    def __init__(self, id, name, dc=0, freq=0):

        super().__init__(id, name, dir=True)

    # Write Duty Cycle
    def write(self, dc=0):
        pass

    # Start PWM
    def start(self, dc=0):
        pass

    # Stop PWM
    def stop(self):
        pass


# ADC class
# Inherit of IO class
class Adc(Io):

    def __init__(self, id, name):

        super().__init__(id, name, dir=False)

    # Read ADC
    def read(self):
        pass

# GPIO Class
# Inherit of IO class
# edge: Edge for automatic detection
# default_value: Default value to write on output gpio
class Gpio(Io):

    def __init__(self, id, name, dir=True, event=None, edge=Edge.BOTH, default_value=False):

        super().__init__(id, name, dir, event)

        self.edge = edge
        self.last_value = None

    # Read the gpio
    def read(self):
        pass

    # Write on the gpio
    def write(self, value):
        pass

    # Launch a thread on _auto_refresh
    def auto_refresh(self, refresh=0.5, callback=None):
        if self.dir:
            return

        Thread(target=self._auto_refresh, args=[refresh, callback]).start()

    # Auto refresh the gpio
    # If the gpio value change according to the edge, it will call the callback
    # Callback need to take 4 args: event, name, id & value
    def _auto_refresh(self, refresh, callback):
        while True:
            sleep(refresh)

            last_value = self.last_value
            new_value = self.read()

            was_updated = new_value != last_value

            if callback is None or last_value is None or not was_updated:
                continue

            if self.edge == Edge.BOTH or self.edge.value == new_value:
                callback(event=self.name if self.event is None else self.event, name=self.name, id=self.id, value=new_value)
