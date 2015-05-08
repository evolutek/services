from time import sleep
from cellaserv.service import Service
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
        print("PMI : start")
        self.move_to_stairs(cs)
        print("PMI : finish")

    def marche_avant(self, x, cs):
        cs.ax["1"].turn(True, self.speed)
        cs.ax["2"].turn(False, self.speed)
        cs.ax["3"].turn(True, self.speed)
        cs.ax["4"].turn(False, self.speed)
        sleep(0.01)
        cs.ax["1"].turn(True, self.speed)
        cs.ax["2"].turn(False, self.speed)
        cs.ax["3"].turn(True, self.speed)
        cs.ax["4"].turn(False, self.speed)
        sleep(x-0.01)
        print("Marche avant : done")

    def marche_arriere(self, x, cs):
        cs.ax["1"].turn(False, self.speed)
        cs.ax["2"].turn(True, self.speed)
        cs.ax["3"].turn(False, self.speed)
        cs.ax["4"].turn(True, self.speed)
        sleep(0.01)
        cs.ax["1"].turn(False, self.speed)
        cs.ax["2"].turn(True, self.speed)
        cs.ax["3"].turn(False, self.speed)
        cs.ax["4"].turn(True, self.speed)
        sleep(x-0.01)
        print("Marche arriere : done")

    def arret(self, x, cs):
        cs.ax["1"].turn(True, 0)
        cs.ax["2"].turn(True, 0)
        cs.ax["3"].turn(True, 0)
        cs.ax["4"].turn(True, 0)
        sleep(0.01)
        cs.ax["1"].turn(True, 0)
        cs.ax["2"].turn(True, 0)
        cs.ax["3"].turn(True, 0)
        cs.ax["4"].turn(True, 0)
        sleep(x-0.01)
        print("Arret : done")

    def rotation_gauche(self, x, cs):
        cs.ax["1"].turn(True, self.speed)
        cs.ax["2"].turn(True, self.speed)
        cs.ax["3"].turn(True, self.speed)
        cs.ax["4"].turn(True, self.speed)
        sleep(0.01)
        cs.ax["1"].turn(True, self.speed)
        cs.ax["2"].turn(True, self.speed)
        cs.ax["3"].turn(True, self.speed)
        cs.ax["4"].turn(True, self.speed)
        sleep(x-0.01)
        print("Rotation gauche : done")

    def rotation_droite(self, x, cs):
        cs.ax["1"].turn(False, self.speed)
        cs.ax["2"].turn(False, self.speed)
        cs.ax["3"].turn(False, self.speed)
        cs.ax["4"].turn(False, self.speed)
        sleep(0.01)
        cs.ax["1"].turn(False, self.speed)
        cs.ax["2"].turn(False, self.speed)
        cs.ax["3"].turn(False, self.speed)
        cs.ax["4"].turn(False, self.speed)
        sleep(x-0.01)
        print("Rotation droite : done")

    def depose_tapis(self, cs):
        cs.ax["5"].move(goal=0)
        sleep(500)
        cs.ax["5"].move(goal=1024)
        cs.ax["5"].move(goal=512)
        print("Depose tapis : done")

    def move_to_stairs(self, cs):
        while self.timer != 6:
            self.marche_avant(1, cs)
            self.timer = self.timer + 1
        self.arret(1, cs)
        self.timer = 0
        while self.timer != 0.5:
            if self.color == -1:
                self.rotation_gauche(0.1, cs)
            else:
                self.rotation_droite(0.1, cs)
            self.timer = self.timer+0.1
        self.arret(1, cs)
        self.marche_avant(6.5, cs)
        self.arret(1, cs)


def main():
    IaPMI()
    print("Roger is Succesful !")

if __name__ == '__main__':
    main()
