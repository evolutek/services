from evolutek.lib.actionqueue import Act_queue as Act_queue
from time import sleep

test = 0

def print_toto(a, b):
    global test
    print("Fonction A: args [", a, "] and [", b, "]")
    test =+ 1
    return test

def print_tata(a, b):
    global test
    print("Fonction B: args [", a, "] and [", b, "]")
    test += 1
    return test

toto = Act_queue()

toto.run_queue()
toto.run_action(print_toto, (1, 2))
toto.run_actions([print_tata, print_toto], [(3, 4), (5, 6)])
toto.run_action(print_toto, (7, 8))
sleep(1)
toto.stop_queue()
while (not toto.response.empty()) :
    print("Stack: ", toto.response.get())
