from time import sleep
from cellaserv.service import Service, Event, Variable, ConfigVariable
from cellaserv.proxy import CellaservProxy


class IaPMI(Service):
    speed = 700
    color = -1
    timer = 0

    def __init__(self):
        cs = CellaservProxy()
        cs.ax["1"].mode_wheel()
        cs.ax["2"].mode_wheel()
        cs.ax["3"].mode_wheel()
        cs.ax["4"].mode_wheel()
        cs.ax["5"].mode_joint()
        print("PMI : Wait")
        match_start = Event('start')
        match_start.wait()
        print("PMI : start")
        self.move_to_stairs()
        print("PMI : finish")

    def marche_avant(self, x, cs):
        cs.ax["1"].turn(True, self.speed)
        cs.ax["2"].turn(False, self.speed)
        cs.ax["3"].turn(True, self.speed)
        cs.ax["4"].turn(False, self.speed)
        sleep(1)
        cs.ax["1"].turn(True, self.speed)
        cs.ax["2"].turn(False, self.speed)
        cs.ax["3"].turn(True, self.speed)
        cs.ax["4"].turn(False, self.speed)
        sleep(x)
        print("Marche avant : done")

    def marche_arriere(self, x, cs):
        cs.ax["1"].turn(False, self.speed)
        cs.ax["2"].turn(True, self.speed)
        cs.ax["3"].turn(False, self.speed)
        cs.ax["4"].turn(True, self.speed)
        sleep(1)
        cs.ax["1"].turn(False, self.speed)
        cs.ax["2"].turn(True, self.speed)
        cs.ax["3"].turn(False, self.speed)
        cs.ax["4"].turn(True, self.speed)
        sleep(x)
        print("Marche arriere : done")

    def arret(self, x, cs):
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

    def rotation_gauche(self, x, cs):
        cs.ax["1"].turn(True, self.speed)
        cs.ax["2"].turn(True, self.speed)
        cs.ax["3"].turn(True, self.speed)
        cs.ax["4"].turn(True, self.speed)
        sleep(1)
        cs.ax["1"].turn(True, self.speed)
        cs.ax["2"].turn(True, self.speed)
        cs.ax["3"].turn(True, self.speed)
        cs.ax["4"].turn(True, self.speed)
        sleep(x)
        print("Rotation gauche : done")

    def rotation_droite(self, x, cs):
        cs.ax["1"].turn(False, self.speed)
        cs.ax["2"].turn(False, self.speed)
        cs.ax["3"].turn(False, self.speed)
        cs.ax["4"].turn(False, self.speed)
        sleep(1)
        cs.ax["1"].turn(False, self.speed)
        cs.ax["2"].turn(False, self.speed)
        cs.ax["3"].turn(False, self.speed)
        cs.ax["4"].turn(False, self.speed)
        sleep(x)
        print("Rotation droite : done")

    def depose_tapis(self, cs):
        cs.ax["5"].move(goal=0)
        sleep(500)
        cs.ax["5"].move(goal=1024)
        cs.ax["5"].move(goal=512)
        print("Depose tapis : done")

    def move_to_stairs(self, cs):
        while self.timer != 6000:
            self.marche_avant(1)
            self.timer = self.timer + 2

        self.arret(1000)
        self.timer = 0
        while self.timer != 1300:
            if self.color == -1:
                self.rotation_gauche(1)
            else:
                self.rotation_droite(1)
            self.timer = self.timer+2
        self.arret(1000)
        self.timer = 0
        while self.timer != 100:
            self.marche_avant(1)
            self.timer = self.timer + 2
            self.marche_avant(1)
            self.timer = self.timer + 2
        self.timer = 0
        while self.timer != 6500:
            if self.timer == 1500:
                self.arret(1)
                self.depose_tapis()
            else:
                self.timer = self.timer + 10
            self.marche_avant(10)


def main():
    IaPMI()
    print("Roger is Succesful !")

if __name__ == '__main__':
    main()
