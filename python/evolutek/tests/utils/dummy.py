from cellaserv.service import Event, Service
from threading import Event
from time import sleep

class Dummy(Service):

    def __init__(self):
        self.need_to_say_something = Event()
        super().__init__()

    @Service.action
    def say_something(self):
        self.need_to_say_something.set()

    @Service.thread
    def loop(self):
        while True:
            self.need_to_say_something.wait()
            self.need_to_say_something.clear()
            self.publish('dummy_start')
            print('Say something')
            self.publish('dummy_stop', status='done', lol='XD')

dummy = Dummy()
dummy.run()
