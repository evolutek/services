from evolutek.lib.component import Component
from evolutek.lib.indicators.lightning_mode import LightningMode, refresh, NB_LOADING_LED
from evolutek.lib.utils.color import Color
from neopixel import NeoPixel, GRB
from threading import Event, Lock, Thread
from time import sleep

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
        self.need_to_stop = Event()

        super().__init__('WS2812BLedStrip', id)

    def __str__(self):
        s = "----------\n"
        s += "%s" % self.name
        s += "Current mode: %s\n" % self.mode.value
        s += "----------"
        return s

    def __dict__(self):
        return {
            "id": self.id,
            "name": self.name,
            "mode": self.mode.value
        }

    def _initialize(self):

        try:
            self.leds = NeoPixel(self.pin, self.nb_leds, brightness=self.brightness)
        except Exception as e:
            print('[%s] Failed to initiliaze Led Strip: %s' % (self.name, str(e)))
            return False

        return True

    def start(self):
        Thread(target=self.run).start()

    def stop(self):
        self.need_to_stop.set()

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
            print('[%s] Setting loading color to: %s' % (self.name, str(color.name)))
            self.loading_color = color

    def run(self):
        while not self.need_to_stop.is_set():
            with self.lock:
                if self.mode == LightningMode.Disabled:
                    for i in range(self.nb_leds):
                        self.leds[i] = Color.Orange.value if self.state ^ i % 2 == 0 else Color.Black.value
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

        self.leds.fill(Color.Black.value)
        self.leds.show()
        print(f"[{self.name}] Stopped")
