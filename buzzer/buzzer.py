#!/usr/bin/env python3

__version__ = "1"

import fcntl
import threading

from cellaserv.service import Service

(PWM_IOCTL_STOP,
PWM_IOCTL_SET_FREQ) = range(0, 2)

class Buzzer(Service):

    __version__ = __version__

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

def main():
    buzzer = Buzzer()
    buzzer.run()

if __name__ == "__main__":
    main()
