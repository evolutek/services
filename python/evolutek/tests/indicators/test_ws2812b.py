import board
from evolutek.lib.indicators.ws2812b import WS2812BLedStrip, LightningMode, Color
from time import sleep

leds = WS2812BLedStrip(42, board.D12, 16, 0.2)
sleep(5)
leds.set_loading_color(Color.Yellow)
sleep(5)
leds.set_mode(LightningMode.Running)
sleep(5)
leds.set_mode(LightningMode.Disabled)
sleep(5)
leds.set_mode(LightningMode.Error)
sleep(5)
