from evolutek.lib.utils.action_queue import ActQueue
from evolutek.lib.utils.task import Task
from evolutek.lib.utils.wrappers import use_queue
from time import sleep

test = 0

def print_toto(a, b):
    global test
    print("Fonction A: args [", a, "] and [", b, "]")
    test =+ 1
    return test

def print_tata(a, b):
    global test
    print("Fonction B: args [", b, "] and [", b, "]")
    test += 1
    return test


def print_test(id):
    print("debut: %d" % id)

def print_test_fin(id, lol):
    print("fin: %d\n====================" % id)

toto = ActQueue(print_test, print_test_fin)
toto.run_queue()
toto.run_action(Task(print_toto, [1, 2]))
"""toto.run_actions([
    Task(print_tata, [3, 4]),
    Task(print_toto, [5, 6])
])"""
toto.run_action(Task(print_toto, {'a' : 1, 'b' : 2}))
toto.run_action(Task(print_toto, [1, 2]))
toto.run_action(Task(print_toto, {'a' : 1, 'b' : 2}))
sleep(1)
toto.stop_queue()

class Test:

    def __init__(self, name):
        self.queue = ActQueue()
        self.queue.run_queue()
        self.name = name

    def stop(self):
        self.queue.stop_queue()

    @use_queue
    def test_use_queue(self):
        print(self.name)

t = Test('Michel')
t.test_use_queue()
sleep(1)
t.test_use_queue(use_queue=False)
sleep(1)
t.stop()
