#!/usr/bin/env python3

from time import sleep
import mraa

mraa.Gpio(2).dir(mraa.DIR_IN)
mraa.Gpio(5).dir(mraa.DIR_IN)
while True:
	if mraa.Gpio(2).read() == 1:
		print("Front")
	if mraa.Gpio(5).read() == 1:
		print("Back")
	sleep(0.5)
