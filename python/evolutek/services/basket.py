from enum import Enum
from threading import Lock

from cellaserv.service import Service

from evolutek.lib.gpio.gpio_factory import GpioType, create_gpio
from evolutek.lib.gpio.gpio import Edge

# TODO:
# * Manage screen

class State(Enum):
    unstarted = "Unstarted"
    started = "Started"
    ended = "Ended"

class Basket(Service):

    def __init__(self):

        self.state = State.unstarted
        self.cherry_count = 0
        self.lock = Lock()

        self.sensor = create_gpio(14, 'sensor', dir=False, edge=Edge.FALLING, type=GpioType.RPI)
        self.sensor.auto_refresh(refresh=0.1, callback=self.counting)

        self.led = create_gpio(15, 'led', dir=True, default_value=False, type=GpioType.RPI)

    @Service.event('match_start')
    @Service.action
    def start(self):
        with self.lock:
            if self.state == State.unstarted:
                self.state = State.started
                print('[BASKET] Starting counting')
    
    @Service.event('match_end')
    @Service.action
    def stop(self):
        with self.lock:
            if self.state == State.started:
                self.state = State.ended
                print('[BASKET] Stoping couting')
    
    @Service.action
    def reset(self):
        with self.lock:
            if self.state == State.ended:
                self.state = State.unstarted
                self.cherry_count = 0
                print('[BASKET] Reseting basket')
    
    @Service.action
    def get_status(self):
        with self.lock:
            return {
                "state": self.state.value,
                "count": self.cherry_count
            }

    @Service.action
    def get_cherry_count(self):
        with self.lock:
            return self.cherry_count
    
    def counting(self):
        with self.lock:
            if self.state == State.started:
                self.cherry_count += 1
                print('[BASKET] Current count: %d' % self.cherry_count)