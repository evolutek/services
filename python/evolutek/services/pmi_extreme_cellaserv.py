import mraa
import time import sleep
import thread
import smbus
import math
from cellaserv.service import Service, Variable, ConfigVariable
from cellaserv.proxy import CellaservProxy

#http://blog.bitify.co.uk/2013/11/reading-data-from-mpu-6050-on-raspberry.html
class IaPMI(Service):
   match_start = Variable('start')
    color = ConfigVariable(section='match', option='color', coerc=lambda v:
            {'green': -1, 'yellow': 1}[v])
    speed_full = ConfigVariable(section='pmi', option='trsl_max', coerc=float)
    speed_slow = ConfigVariable(section='pmi', option='trsl_min', coerc=float) 
    LIBDXL_PATH = [".", "/usr/lib"]

    LIBDXL_PATH_ENV = os.environ.get("LIBDXL_PATH", None)
    if LIBDXL_PATH_ENV:
        LIBDXL_PATH.insert(0, LIBDXL_PATH_ENV)
        speed =  ConfigVariable(section='pmi', option='trsl_max', coerc=float)

    #Code for MPU 6050
    def read_byte(adr):
        return bus.read_byte_data(address, adr)

    def read_word(adr):
        high = bus.read_byte_data(address, adr)
        low = bus.read_byte_data(address, adr+1)
        val = (high << 8) + low
        return val

    def dist(a,b):
        return math.sqrt((a*a)+(b*b))

    def read_word_2c(adr):
        val = read_word(adr)
        if (val >= 0x8000):
            return -((65535 - val) + 1)
        else:
            return val

    def get_y_rotation(x,y,z):
        radians = math.atan2(x, dist(y,z))
        return -math.degrees(radians)

    def get_x_rotation(x,y,z):
        radians = math.atan2(y, dist(x,z))
        return math.degrees(radians)

    def get_z_rotation(x,y,z):
        radians = math.atan2(z, dist(x,y))
        return math.degrees(radians)

    def dist(a,b):
        return math.sqrt((a*a)+(b*b))

    #Code for Ax 12
    def marche_avant(float(x)):
        cs.ax["1"].turn(True,speed)
        cs.ax["2"].turn(False,speed)
        cs.ax["3"].turn(True,speed)
        cs.ax["4"].turn(False,speed)
        time.sleep(1)
        cs.ax["1"].turn(True,speed)
        cs.ax["2"].turn(False,speed)
        cs.ax["3"].turn(True,speed)
        cs.ax["4"].turn(False,speed)
        time.sleep(x)
        print("Marche avant : done")
    

    def marche_arriere(float(x)):
        cs.ax["1"].turn(False,speed)
        cs.ax["2"].turn(True,speed)
        cs.ax["3"].turn(False,speed)
        cs.ax["4"].turn(True,speed)
        time.sleep(1)
        cs.ax["1"].turn(False,speed)
        cs.ax["2"].turn(True,speed)
        cs.ax["3"].turn(False,speed)
        cs.ax["4"].turn(True,speed)
        time.sleep(x)
        print("Marche arriere : done")
    

    def arret(float(x)):
        cs.ax["1"].turn(True,0)
        cs.ax["2"].turn(True,0)
        cs.ax["3"].turn(True,0)
        cs.ax["4"].turn(True,0)
        time.sleep(1)
        cs.ax["1"].turn(True,0)
        cs.ax["2"].turn(True,0)
        cs.ax["3"].turn(True,0)
        cs.ax["4"].turn(True,0)
        time.sleep(x)
        print("Arret : done")


    def rotation_gauche(float(x)):
        cs.ax["1"].turn(True,speed)
        cs.ax["2"].turn(True,speed)
        cs.ax["3"].turn(True,speed)
        cs.ax["4"].turn(True,speed)
        time.sleep(1)
        cs.ax["1"].turn(True,speed)
        cs.ax["2"].turn(True,speed)
        cs.ax["3"].turn(True,speed)
        cs.ax["4"].turn(True,speed)
        time.sleep(x)
        print("Rotation gauche : done")

    def rotation_droite(float(x)):
        cs.ax["1"].turn(False,speed)
        cs.ax["2"].turn(False,speed)
        cs.ax["3"].turn(False,speed)
        cs.ax["4"].turn(False,speed)
        time.sleep(1)
        cs.ax["1"].turn(False,speed)
        cs.ax["2"].turn(False,speed)
        cs.ax["3"].turn(False,speed)
        cs.ax["4"].turn(False,speed)
        time.sleep(x)
        print("Rotation droite : done")

    def depose_tapis():
        cs.ax["5"].move(goal=0)
        time.sleep(500)
        cs.ax["5"].move(goal=1024)
        print("Depose tapis : done")

    #this thread manage when you have to dodge   
    def dodge ( threadName,ping,pind, is_activated):
        while(True):
            if(!is_activated):
                need_to_dodge = false
            else:
                need_to_dodge = ((mraa.read(ping).read() < 100)or(mraa.read(pind).read() < 100))


    #this thread tell you wh...oh wait           
    def tirette (threadName,pin):
        while(True):
            need_to_stop = (mraa.read(pin).read() > 512)

    #IA part
    def move_to_stairs(self):
        while timer != 6000:
            while need_to_stop:
                arret(1); # if sharps those not work test acquisition time
            marche_avant(1)
            timer = timer + 2;

        arret(1000)
        timer = 0
        while timer != 1300:
            while need_to_stop:
                arret(1)
            if color == -1:
                rotation_gauche(1)
            else:
                rotation_droite(1)
            timer = timer+2
        arret(1000)
        timer = 0
        while timer != 100:
            while need_to_stop:
                arret(1)
            marche_avant(1)
            timer = timer + 2
            marche_avant(1)
            timer = timer + 2
        timer = 0
        while(get_z_rotation(accel_xout_scaled,accel_yout_scaled,accel_zout_scaled) > -120):
            print(get_z_rotation(accel_xout_scaled,accel_yout_scaled,accel_zout_scaled))
            if timer == 1500:
                arret(1)
                depose_tapis()
            else:
                timer = timer + 10
            marche_avant(10)
        
    #Load all library    
    libdxl = None
    for path in LIBDXL_PATH:
        try:
            libdxl = ctypes.CDLL(path + "/libdxl.so")
            except:
                pass
        if not libdxl:
            raise RuntimeError("Cannot load libdxl.so, check LIBDXL_PATH")
        self.dxl = libdxl
        ret = self.dxl.dxl_initialize(DEVICE_ID, BAUD_RATE)
        if ret != 1:
            raise RuntimeError("Cannot initialize device")

    # Power management registers MPU6050
    power_mgmt_1 = 0x6b
    power_mgmt_2 = 0x6c
    bus = smbus.SMBus(0) # or bus = smbus.SMBus(1) for Revision 2 boards
    address = 0x68       # This is the address value read via the i2cdetect command

def main():
     # Now wake the 6050 up as it starts in sleep mode
    bus.write_byte_data(address, power_mgmt_1, 0)
    gyro_xout = read_word_2c(0x43)
    gyro_yout = read_word_2c(0x45)
    gyro_zout = read_word_2c(0x47)
    accel_xout_scaled = accel_xout / 16384.0
    accel_yout_scaled = accel_yout / 16384.0
    accel_zout_scaled = accel_zout / 16384.0
    speed = 700
    is_yellow = True
    timer = 0
    thread.start_new_thread(dodge,("ThreadScharp",10,11))
    thread.start_new_thread(tirette,("ThreadTirette",15))
    #init ax12 lib
    cs = CellaservProxy()
    cs.ax["1"].mode_wheel()
    cs.ax["2"].mode_wheel()
    cs.ax["3"].mode_wheel()
    cs.ax["4"].mode_wheel()
    cs.ax["5"].mode_joint()
    #test if the cord is connected
    while(need_to_stop):
        time.sleep(10)
    print("PMI : start")
    move_to_stairs()
    print("PMI : finish")

if __name__ == '__main__':
    main()


    
    


