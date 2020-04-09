## TODO : manage other options
## TODO : manage available gpio 

BCM = 'BCM'
IN  = 'IN'
OUT = 'OUT'
LOW = 'LOW'
HIGH = 'HIGH'
PUD_DOWN = 'PULL DOWN'

def setmode(cls, mode):
    print('[FAKE_GPIO] Setting mode %s' % mode)

def setup(cls, id, mode, initial, pull_up_down=None):
    print('[FAKE_GPIO] Setting gpio %d: (%s, %s)' % (id, mode, initial))

def input(id):
    print('[FAKE_GPIO] Reading gpio %d' % id)
    return False

def output(id, value)
    print('[FAKE_GPIO] Writing on gpio %d: %s' % (id, value))]

class PWM:

    def __init__(self, id, freq):
        self.id = id
        print('[FAKE_GPIO] Init pwm: (%d; %d)' % (id, freq))

    def ChangeDutyCycle(dc):
        print('[FAKE_GPIO] Changing duty cycle on pwm %d: %d' % (self.id, dc))

    def start(dc):
        print('[FAKE_GPIO] Strating pwm %d: %d' % (self.id, dc))

    def stop():
        print('[FAKE_GPIO] Stoping pwm %d' % self.id)
