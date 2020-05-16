from cellaserv.service import Service
from evolutek.lib.gpio import Gpio
from time import sleep

class Test_Gpio(Service):

    def __init__(self):
        self.gpio = Gpio(42, "my_gpio", dir=False, event="Auto refresh")

        super().__init__()

        self.gpio.auto_refresh(1, self.publish)

    @Service.thread
    def loop(self):
        while True:
            print("Loop read: %d" % self.gpio.read())
            sleep(0.5)

def main():
    test_gpio = Test_Gpio()
    test_gpio.run()

if __name__ == "__main__":
    main()
