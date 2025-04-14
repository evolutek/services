from cellaserv.service import Service
from evolutek.lib.gpio.gpio_factory import create_gpio
from time import sleep

class Test_Gpio(Service):

    def __init__(self):
        self.gpio = create_gpio(17, "tirette", dir=False, event="Tirette")

        super().__init__()

        self.gpio.auto_refresh(callback=self.publish)

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
