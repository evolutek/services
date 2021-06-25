from cellaserv.service import Event, Service
from evolutek.lib.status import RobotStatus
from threading import Event
from time import sleep

class Dummy(Service):

    def __init__(self):
        self.need_to_say_something = Event()
        self.current_id = 0
        super().__init__()

    @Service.action
    def say_something(self):
        self.need_to_say_something.set()
        return self.current_id

    @Service.thread
    def loop(self):
        while True:
            self.need_to_say_something.wait()
            self.need_to_say_something.clear()
            self.publish('dummy_start', id=self.current_id)
            sleep(1)
            print('Say something')
            self.publish('dummy_stop', **RobotStatus.return_status(RobotStatus.Done, lol='XD', id=self.current_id))
            self.current_id += 1

dummy = Dummy()
dummy.run()
