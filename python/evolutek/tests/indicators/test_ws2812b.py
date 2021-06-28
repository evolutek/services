import board
from evolutek.lib.indicators.ws2812b import WS2812BLedStrip, LightningMode
from evolutek.lib.utils.color import Color
from time import sleep

leds = WS2812BLedStrip(42, board.D12, 26, 0.1)
leds.start()
sleep(5)
leds.set_loading_color(Color.Yellow)
sleep(5)
leds.set_mode(LightningMode.Running)
sleep(5)
leds.set_mode(LightningMode.Disabled)
sleep(5)
leds.set_mode(LightningMode.Error)
sleep(5)
leds.stop()