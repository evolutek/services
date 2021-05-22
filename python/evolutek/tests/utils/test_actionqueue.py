from evolutek.lib.utils.action_queue import ActQueue
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

toto = ActQueue()

toto.run_queue()
toto.run_action(print_toto, (1, 2))
toto.run_actions([print_tata, print_toto], [(3, 4), (5, 6)])
toto.run_action(print_toto, (7, 8))
sleep(1)
toto.stop_queue()
while (not toto.response_queue.empty()) :
    print("Stack: ", toto.response_queue.get())
