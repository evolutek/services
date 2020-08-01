from evolutek.services.actuators import Buoy, PumpActuator

from time import sleep

class TestPump:

    def __init__(self):

        self.pumps = [
            PumpActuator(27, 18, 1),
            PumpActuator(22, 23, 2),
            PumpActuator(9, 24, 3),
            PumpActuator(11, 25, 4),
            PumpActuator(5, 8, 5),
            PumpActuator(6, 7, 6),
            PumpActuator(19, 16, 7),
            PumpActuator(26, 20, 8)
        ]

        for i in range(len(self.pumps)):
            self.test_pump(i)

    def test_pump(self, id):

        print('[TEST] Testing pump %d' % id)
        pump = self.pumps[id]
        print(pump)

        sleep(2)

        print('[TEST] Getting Buoy')
        pump.pump_get()
        print(pump)

        sleep(2)

        print('[TEST] Setting buoy')
        pump.pump_set(Buoy.Green)
        print(pump)

        sleep(2)

        print('[TEST] Drop buoy')
        pump.pump_drop()
        print(pump)

        sleep(2)

def main():
    test = TestPump()

if __name__ == '__main__':
    main()
