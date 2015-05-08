from time import sleep
from threading import Timer
from cellaserv.service import Service, Event
from cellaserv.proxy import CellaservProxy


class IaPMI(Service):
    speed = 700
    color = -1
    timer = 0
    cs = CellaservProxy()

    def __init__(self):
        self.cs.ax["1"].mode_wheel()
        self.cs.ax["2"].mode_wheel()
        self.cs.ax["3"].mode_wheel()
        self.cs.ax["4"].mode_wheel()
        self.cs.ax["5"].mode_joint()
        print("PMI : Wait")
        Event('start').wait()
        self.match_stop_timer = Timer(85, self.match_stop)
        Event('pmi_start').wait()
        print("PMI : start")
        self.move_to_stairs()
        print(self.match_stop_timer)
        print("PMI : finish")

    def marche_avant(self, x):
        print(self.match_stop_timer)
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
        print(self.match_stop_timer)
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
        print(self.match_stop_timer)
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
        print(self.match_stop_timer)
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
        print(self.match_stop_timer)
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
        print(self.match_stop_timer)
        self.cs.ax["5"].move(goal=0)
        sleep(500)
        self.cs.ax["5"].move(goal=1024)
        self.cs.ax["5"].move(goal=512)
        print("Depose tapis : done")

    def move_to_stairs(self):
        print(self.match_stop_timer)
        while self.timer != 6:
            self.marche_avant(1)
            self.timer = self.timer + 1
        self.arret(1)
        self.timer = 0
        while self.timer != 0.5:
            if self.color == -1:
                self.rotation_gauche(0.1)
            else:
                self.rotation_droite(0.1)
            self.timer = self.timer+0.1
        self.arret(1)
        self.time = 0
        while self.timer != 6.5:
            if self.timer == 1.5:
                self.arret(1)
                self.depose_tapis()
                self.arret(1)
            self.marche_avant(0.5)
            self.timer = self.timer + 0.5
        self.arret(1)

    def match_stop(self):
        self.arret(1)
        self.cs.ax["1"].free()
        self.cs.ax["2"].free()
        self.cs.ax["3"].free()
        self.cs.ax["4"].free()
        self.cs.ax["5"].free()
        print("Roger died of boreness ...")
        del self


def main():
    IaPMI()
    print("Roger is Succesful !")

if __name__ == '__main__':
    main()
