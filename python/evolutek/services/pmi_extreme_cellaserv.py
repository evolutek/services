from time import sleep
from cellaserv.service import Service
from threading import Timer, Event
from cellaserv.proxy import CellaservProxy


class IaPMI(Service):
    speed = 700
    color = 1 # 1 vert -1 jaune
    timer = 0

    def __init__(self):
        super().__init__()
        self.color = 1
        self.set_move = Event()
        self.sharp_timer = Timer(1.0, self.set_move.clear)
        self.cs = CellaservProxy()
        self.cs.ax["1"].mode_wheel()
        self.cs.ax["2"].mode_wheel()
        self.cs.ax["3"].mode_wheel()
        self.cs.ax["4"].mode_wheel()
        self.cs.ax["5"].mode_joint()
        print('wait')

    @Service.event
    def match_start(self, color_):
        self.match_timer = Timer(85.0, self.match_stop)
        self.match_timer.start()
        self.color = int(color_)
        print('wait for pal')

    @Service.event
    def pmi_start(self):
        self.move_to_stairs()

    @Service.event
    def sharp_avoid(self):
        print('sharp')
        try:
            self.sharp_timer.cancel()
        except:
            print('no timer started')
        self.set_move.set()
        self.sharp_timer = Timer(1.0, self.set_move.clear)
        self.sharp_timer.start()

    def marche_avant(self, x):
        self.cs.ax["1"].turn(True, self.speed)
        self.cs.ax["2"].turn(False, self.speed)
        self.cs.ax["3"].turn(True, self.speed)
        self.cs.ax["4"].turn(False, self.speed)
        sleep(0.01)
        self.cs.ax["1"].turn(True, self.speed)
        self.cs.ax["2"].turn(False, self.speed)
        self.cs.ax["3"].turn(True, self.speed)
        self.cs.ax["4"].turn(False, self.speed)
        sleep(x-0.01)
        print("Marche avant : done")

    def marche_arriere(self, x):
        self.cs.ax["1"].turn(False, self.speed)
        self.cs.ax["2"].turn(True, self.speed)
        self.cs.ax["3"].turn(False, self.speed)
        self.cs.ax["4"].turn(True, self.speed)
        sleep(0.01)
        self.cs.ax["1"].turn(False, self.speed)
        self.cs.ax["2"].turn(True, self.speed)
        self.cs.ax["3"].turn(False, self.speed)
        self.cs.ax["4"].turn(True, self.speed)
        sleep(x-0.01)
        print("Marche arriere : done")

    def arret(self, x):
        self.cs.ax["1"].turn(True, 0)
        self.cs.ax["2"].turn(True, 0)
        self.cs.ax["3"].turn(True, 0)
        self.cs.ax["4"].turn(True, 0)
        sleep(0.01)
        self.cs.ax["1"].turn(True, 0)
        self.cs.ax["2"].turn(True, 0)
        self.cs.ax["3"].turn(True, 0)
        self.cs.ax["4"].turn(True, 0)
        sleep(x-0.01)
        print("Arret : done")

    def rotation_gauche(self, x):
        self.cs.ax["1"].turn(True, self.speed)
        self.cs.ax["2"].turn(True, self.speed)
        self.cs.ax["3"].turn(True, self.speed)
        self.cs.ax["4"].turn(True, self.speed)
        sleep(0.01)
        self.cs.ax["1"].turn(True, self.speed)
        self.cs.ax["2"].turn(True, self.speed)
        self.cs.ax["3"].turn(True, self.speed)
        self.cs.ax["4"].turn(True, self.speed)
        sleep(x-0.01)
        print("Rotation gauche : done")

    def rotation_droite(self, x):
        self.cs.ax["1"].turn(False, self.speed)
        self.cs.ax["2"].turn(False, self.speed)
        self.cs.ax["3"].turn(False, self.speed)
        self.cs.ax["4"].turn(False, self.speed)
        sleep(0.01)
        self.cs.ax["1"].turn(False, self.speed)
        self.cs.ax["2"].turn(False, self.speed)
        self.cs.ax["3"].turn(False, self.speed)
        self.cs.ax["4"].turn(False, self.speed)
        sleep(x-0.01)
        print("Rotation droite : done")

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
            while self.set_move.is_set():
                self.arret(0.5)
                print('stop')
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
        self.cs.ax["1"].free()
        self.cs.ax["2"].free()
        self.cs.ax["3"].free()
        self.cs.ax["4"].free()
        self.cs.ax["5"].free()
        print("Roger died of boreness ...")
        del self


def main():
    Roger = IaPMI()
    Roger.run()
    print("Roger is Succesful !")

if __name__ == '__main__':
    main()
