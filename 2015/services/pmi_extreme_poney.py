from time import sleep
from cellaserv.service import Service
from threading import Timer, Event
from cellaserv.proxy import CellaservProxy


class IaPMI(Service):
    speed = 700
    color = 1 # 1 vert -1 jaune
    timer = 0
    need_to_dodge = False
    should_avoid = True

    def __init__(self):
        super().__init__()
        self.cs = CellaservProxy()
        for n in [1,2,3,4]:
            self.cs.ax[str(n)].mode_wheel()
        self.cs.ax["5"].mode_joint()
        print('wait')

    @Service.event
    def match_start(self):
        self.match_timer = Timer(85.0, self.match_stop())
        self.match_timer.start()
        print('wait for pal')

    @Service.event
    def pmi_start(self):
        self.move_to_stairs()

    @Service.event
    def sharp_avoid(self):
        print('sharp')
        need_to_dodge = should_avoid

    def marche_avant(self, x):
        moove(self,x,[True,False]*2,self.speed)
        print("Marche avant : done")

    def marche_arriere(self, x):
        moove(self,x,[False,True]*2,self.speed)
        print("Marche arriere : done")

    def arret(self,x):
        for n in [1,2]:
            for i in [1,2,3,4] :
                self.cs.ax[str(i)].turn(True, 0)
            sleep(0.01)
        sleep(x-0.01)
        print("Arret : done")

    def moove(self, x, direction,speed):
        time = 0
        time_start = time.time()
        while time < x :
            while need_to_dodge :
                arret(0)
                need_to_dodge = False
            for i in [0,1]:
                for n in [1,2,3,4]:
                    self.cs.ax[str(n)].turn(direction[n-1],speed)
                # sleep(0.01)
                time = time + (time_start - time.time())
                
        
        print("Rotation gauche : done")

    def rotation_gauche (self,x):
        moove(self,x,[True]*4,self.speed)

    def rotation_droite(self, x):
        moove(self,x,[False]*4,self.speed)
        
    def depose_tapis(self):
        self.cs.ax["5"].move(goal=375)
        sleep(2)
        self.cs.ax["5"].move(goal=1000)
        sleep(2)
        self.cs.ax["5"].move(goal=700)
        print("Depose tapis : done")

    def move_to_stairs(self):
        print("PMI : start")
        while self.timer <= 1.6:
            self.marche_avant(0.05)
            self.timer = self.timer + 0.05
        self.arret(1)
        self.timer = 0
        while self.timer <= 0.2:
            if self.color == -1:
                self.rotation_gauche(0.05)
            else:
                self.rotation_droite(0.05)
            self.timer = self.timer+0.05
        should_avoid = False
        self.arret(1)
        self.timer = 0
        while self.timer <= 5:
            if self.timer == 4.5:
                self.arret(1)
                self.depose_tapis()
                self.arret(1)
            self.marche_avant(0.5)
            self.timer = self.timer + 0.5
        self.arret(1)
        while True:
            print('Roger is bored')
            sleep(1)

    def match_stop(self):
        self.arret(1)
        self.cs.ax["5"].move(goal=700)
        for n in [1,2,3,4,5]:
            self.cs.ax[sr(n)].free()
        print("Roger died of boreness ...")
        del self


def main():
    Roger = IaPMI()
    Roger.run()
    print("Roger is Succesful !")

if __name__ == '__main__':
    main()
