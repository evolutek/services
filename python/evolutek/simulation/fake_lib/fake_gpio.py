## TODO : manage other options
## TODO : manage available gpio

BCM = 'BCM'
IN  = 'IN'
OUT = 'OUT'
LOW = 'LOW'
HIGH = 'HIGH'
PUD_DOWN = 'PULL DOWN'

def setmode(mode):
    print('[FAKE_GPIO] Setting mode %s' % mode)

def setup(id, mode, initial=LOW, pull_up_down=None):
    print('[FAKE_GPIO] Setting gpio %d: %s' % (id, mode))

def input(id):
    print('[FAKE_GPIO] Reading gpio %d' % id)
    return 0

def output(id, value):
    print('[FAKE_GPIO] Writing on gpio %d: %s' % (id, value))

class PWM:

    def __init__(self, id, freq):
        self.id = id
        print('[FAKE_GPIO] Init pwm: (%d; %d)' % (id, freq))

    def ChangeDutyCycle(self, dc):
        print('[FAKE_GPIO] Changing duty cycle on pwm %d: %d' % (self.id, dc))

    def start(self, dc):
        print('[FAKE_GPIO] Strating pwm %d: %d' % (self.id, dc))

    def stop(self):
        print('[FAKE_GPIO] Stoping pwm %d' % self.id)
