#!/usr/bin/env python3

import fcntl
import threading
import time

from cellaserv.service import Service

(PWM_IOCTL_STOP,
PWM_IOCTL_SET_FREQ) = range(0, 2)

class Buzzer(Service):

    def __init__(self):
        super().__init__()
        self._pwm = open('/dev/pwm')

    @Service.action
    def freq(self, freq):
        fcntl.ioctl(self._pwm, PWM_IOCTL_SET_FREQ, int(freq))

    @Service.action
    def freq_seconds(self, freq, seconds):
        self.freq(freq)
        self.t = threading.Timer(float(seconds), self.stop)
        self.t.start()

    @Service.action
    def stop(self):
        fcntl.ioctl(self._pwm, PWM_IOCTL_STOP)

    @Service.event
    def beep_ok(self):
        self.freq_seconds(freq=4, seconds=.5)

    @Service.event
    def beep_ko(self):
        self.freq_seconds(freq=200, seconds=.5)

    @Service.event
    def beep_ready(self):
        for f in range(2000, 4000, 50):
            self.freq(f)
            time.sleep(.04)

        self.stop()

    @Service.event
    def beep_down(self):
        for f in range(4000, 2000, -50):
            self.freq(f)
            time.sleep(.04)

        self.stop()

def main():
    buzzer = Buzzer()
    buzzer.run()

if __name__ == "__main__":
    main()
