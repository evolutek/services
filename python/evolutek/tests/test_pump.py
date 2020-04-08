from evolutek.lib.actuators import Buoy, PumpActuator

from time import sleep

class TestPump:

    def __init__(self):

        self.pumps = [
            PumpActuator(27, 18, 1),
            PumpActuator(22, 23, 2),
            PumpActuator(10, 24, 3),
            PumpActuator(9, 25, 4),
            PumpActuator(11, 24, 5),
            PumpActuator(5, 7, 6),
            PumpActuator(6, 16, 7),
            PumpActuator(19, 20, 8)
        ]

        for i in range(len(self.pumps)):
            self.test_pump(i)

    def test_pump(self, id):

        print('[TEST] Testing pump %d' % id)
        pump = self.pumps(id)
        print(pump)

        print('[TEST] Getting Buoy')
        pump.get_buoy()
        print(pump)

        print('[TEST] Setting buoy')
        pump.set_buoy(Buoy.Green)
        print(pump)

        print('[TEST] Drop buoy')
        pump.drop_buoy()
        print(pump)

def main():
    test = TestPump()

if __name__ == '__main__':
    main()
