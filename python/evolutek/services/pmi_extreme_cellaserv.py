import mraa
from time import sleep
import thread
from cellaserv.service import Service, Event, Variable, ConfigVariable
from cellaserv.proxy import CellaservProxy

# http://blog.bitify.co.uk/2013/11/reading-data-from-mpu-6050-on-raspberry.html


class IaPMI(Service):
    # match_start = Variable('start')
    color = ConfigVariable(section='match', option='color',  coerc=lambda v: {'green': -1, 'yellow': 1}[v])
    speed = ConfigVariable(section='pmi', option='trsl_max', coerc=float)

    # Code for Ax 12
    # 1 = droite_avant
    # 2 = gauche_arriere
    # 3 = droite_arriere
    # 4 = gauche_avant

    def __init__(self):
        timer = 0
        # thread.start_new_thread(dodge,("ThreadScharp",10,11))
        # thread.start_new_thread(tirette,("ThreadTirette",15))
        # init ax12 lib
        cs = CellaservProxy()
        cs.ax["1"].mode_wheel()
        cs.ax["2"].mode_wheel()
        cs.ax["3"].mode_wheel()
        cs.ax["4"].mode_wheel()
        cs.ax["5"].mode_joint()
        # test if the cord is connected
        # while(need_to_dodge):
        # time.sleep(10)
        print("PMI : Wait")
        match_start = Event('start')
        match_start.wait()
        print("PMI : start")
        move_to_stairs()
        print("PMI : finish")

    def marche_avant(x):
        cs.ax["1"].turn(True, speed)
        cs.ax["2"].turn(False, speed)
        cs.ax["3"].turn(True, speed)
        cs.ax["4"].turn(False, speed)
        sleep(1)
        cs.ax["1"].turn(True, speed)
        cs.ax["2"].turn(False, speed)
        cs.ax["3"].turn(True, speed)
        cs.ax["4"].turn(False, speed)
        sleep(x)
        print("Marche avant : done")

    def marche_arriere(x):
        cs.ax["1"].turn(False, speed)
        cs.ax["2"].turn(True, speed)
        cs.ax["3"].turn(False, speed)
        cs.ax["4"].turn(True, speed)
        sleep(1)
        cs.ax["1"].turn(False, speed)
        cs.ax["2"].turn(True, speed)
        cs.ax["3"].turn(False, speed)
        cs.ax["4"].turn(True, speed)
        sleep(x)
        print("Marche arriere : done")

    def arret(x):
        cs.ax["1"].turn(True, 0)
        cs.ax["2"].turn(True, 0)
        cs.ax["3"].turn(True, 0)
        cs.ax["4"].turn(True, 0)
        sleep(1)
        cs.ax["1"].turn(True, 0)
        cs.ax["2"].turn(True, 0)
        cs.ax["3"].turn(True, 0)
        cs.ax["4"].turn(True, 0)
        sleep(x)
        print("Arret : done")

    def rotation_gauche(x):
        cs.ax["1"].turn(True, speed)
        cs.ax["2"].turn(True, speed)
        cs.ax["3"].turn(True, speed)
        cs.ax["4"].turn(True, speed)
        sleep(1)
        cs.ax["1"].turn(True, speed)
        cs.ax["2"].turn(True, speed)
        cs.ax["3"].turn(True, speed)
        cs.ax["4"].turn(True, speed)
        sleep(x)
        print("Rotation gauche : done")

    def rotation_droite(x):
        cs.ax["1"].turn(False, speed)
        cs.ax["2"].turn(False, speed)
        cs.ax["3"].turn(False, speed)
        cs.ax["4"].turn(False, speed)
        sleep(1)
        cs.ax["1"].turn(False, speed)
        cs.ax["2"].turn(False, speed)
        cs.ax["3"].turn(False, speed)
        cs.ax["4"].turn(False, speed)
        sleep(x)
        print("Rotation droite : done")

    def depose_tapis():
        cs.ax["5"].move(goal=0)
        sleep(500)
        cs.ax["5"].move(goal=1024)
        cs.ax["5"].move(goal=512)
        print("Depose tapis : done")

    # this thread manage when you have to dodge
   """ def dodge ( threadName,ping,pind, is_activated):
        while(True):
            if(!is_activated):
                need_to_dodge = false
            else:
                need_to_dodge = ((mraa.read(ping).read() < 100)or(mraa.read(pind).read() < 100))
"""

    

    #this thread tell you wh...oh wait
    #def tirette (threadName,pin):
    #   while(True):
    #       need_to_dodge = (mraa.read(pin).read() > 512)

    #IA part
    def move_to_stairs(self):
        while timer != 6000:
            #while need_to_dodge:
                #arret(1); # if sharps those not work test acquisition time
            marche_avant(1)
            timer = timer + 2;

        arret(1000)
        timer = 0
        while timer != 1300:
            #while need_to_dodge:
               # arret(1)
            if color == -1:
                rotation_gauche(1)
            else:
                rotation_droite(1)
            timer = timer+2
        arret(1000)
        timer = 0
        while timer != 100:
            #while need_to_dodge:
               # arret(1)
            marche_avant(1)
            timer = timer + 2
            marche_avant(1)
            timer = timer + 2
        timer = 0
        while timer != 6500:
            if timer == 1500:
                arret(1)
                depose_tapis()
            else:
                timer = timer + 10
            marche_avant(10)

def main():
    Roger = IaPMI()
    print("Roger is Succesful !")

if __name__ == '__main__':
    main()
