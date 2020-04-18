from evolutek.lib.lma import launch_multiple_actions
from time import sleep

class Test_Lam:

    def __init__(self):

        print('[TEST] Starting test')

        res = launch_multiple_actions([wait, wait], [[5], [2]])

        if res[0] != 5:
            print('[TEST] First action return bad value: %d' % res[0])

        if res[1] != 2:
            print('[TEST] Second action return bad value: %d' % res[1])

        print('[TEST] Ending test')

def wait(t):
    sleep(t)
    return t

def main():
    test_lam = Test_Lam()

if __name__ == "__main__":
    main()
