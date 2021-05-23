from enum import Enum
from evolutek.lib.component import Component
from neopixel import NeoPixel, GRB
from threading import Lock, Thread
from time import sleep

class LightningMode(Enum):
    Disabled = 'disabled'
    Error = 'error'
    Loading = 'loading'
    Running = 'running'

refresh = {
    LightningMode.Disabled : 0.5,
    LightningMode.Error : 0.5,
    LightningMode.Loading : 0.1,
    LightningMode.Running  : 1
}

NB_LOADING_LED = 3

class Color(Enum):
    Black = (0, 0, 0)
    Blue = (0, 0, 255)
    Green = (0, 255, 0)
    Orange = (255, 10, 0)
    Red = (255, 0, 0)
    Yellow = (255, 255, 0)


class WS2812BLedStrip(Component):

    def __init__(self, id, pin, nb_leds, brightness):
        self.pin = pin
        self.nb_leds = nb_leds
        self.brightness = brightness
        self.lock = Lock()
        self.mode = LightningMode.Loading
        self.loading_color = Color.Blue

        self.current_led = 0
        self.state = False

        super().__init__('WS2812BLedStrip', id)

    def __str__(self):
        s = "----------\n"
        s += "%s" % self.name
        s += "Current mode: %s" % self.mode.value
        s += "----------"
        return s

    def _initialize(self):

        try:
            self.leds = NeoPixel(self.pin, self.nb_leds, brightness=10)
        except Exception as e:
            print('[%s] Failed to initiliaze Led Strip: %s' % (self.name, str(e)))
            return False

        Thread(target=self.run).start()

        return True

    def set_mode(self, mode=LightningMode.Loading):
        with self.lock:

            print('[%s] Setting mode to: %s' % (self.name, mode.value))

            self.mode = mode

            self.leds.fill(Color.Black.value)

            if self.mode == LightningMode.Loading:
                self.current_led = self.nb_leds - 1
                for i in range(NB_LOADING_LED):
                    self.leds[i] = self.loading_color.value

            elif self.mode == LightningMode.Disabled or self.mode == LightningMode.Error:
                self.state = False

            self.leds.show()

    def set_loading_color(self, color):
        with self.lock:
            print('[%s] Setting loading color to: %s' % (self.name, str(color.value)))
            self.loading_color = color

    def run(self):
        while True:
            with self.lock:

                if self.mode == LightningMode.Disabled:
                    self.leds.fill(Color.Orange.value if self.state else Color.Black.value)
                    self.state = not self.state

                elif self.mode == LightningMode.Error:
                    self.leds.fill(Color.Red.value if self.state else Color.Black.value)
                    self.state = not self.state

                elif self.mode == LightningMode.Loading:
                    self.leds[self.current_led] = Color.Black.value
                    self.leds[(self.current_led + NB_LOADING_LED) % self.nb_leds] = self.loading_color.value
                    self.current_led = (self.current_led + 1) % self.nb_leds

                elif self.mode == LightningMode.Running:
                    self.leds.fill(Color.Green.value)

                self.leds.show()

            sleep(refresh[self.mode])
