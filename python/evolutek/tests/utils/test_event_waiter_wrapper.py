from cellaserv.proxy import CellaservProxy
from cellaserv.service import Event, Service
from evolutek.lib.utils.wrappers import event_waiter
from time import sleep

class Test(Service):

    start_event = Event(set='dummy_start')
    stop_event = Event(set='dummy_stop')

    def __init__(self):
        self.cs = CellaservProxy()

        self.say = event_waiter(self.cs.dummy.say_something, callback=self.callback)
        super().__init__()

    def callback(self):
        print('Callback called')
        return False

    @Service.thread
    def test(self):
        print(self.say(self))


test = Test()
test.run()