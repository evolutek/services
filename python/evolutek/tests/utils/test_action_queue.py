from evolutek.lib.utils.action_queue import ActQueue
from evolutek.lib.utils.task import Task
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


def print_test():
    print("debut")

def print_test_fin(lol):
    print("fin\n====================")

toto = ActQueue(print_test, print_test_fin)
toto.run_queue()
toto.run_action(Task(print_toto, [1, 2]))
toto.run_actions([
    Task(print_tata, [3, 4]),
    Task(print_toto, [5, 6])
])
toto.run_action(Task(print_toto, {'a' : 1, 'b' : 2}))
sleep(1)
toto.stop_queue()
