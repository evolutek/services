#!/usr/bin/env python3
from time import sleep

from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service

AX_ID_PINCE_GAUCHE = "1"
AX_ID_PINCE_DROITE = "6"
AX_ID_ASCENSSEUR = "2"
AX_ID_ROUE_GAUCHE = "5"
AX_ID_ROUE_DROITE = "3"

DELAY = 0.1

class PMI(Service):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cs = CellaservProxy(self)

    @Serivce.action
    def reset(self):
        self.cs.ax[AX_ID_ASCENSSEUR].mode_joint()
        self.cs.ax[AX_ID_ROUE_GAUCHE].mode_wheel()
        self.ouvrir_pinces()
        self.ascensseur_bas()

    @Service.action
    def ouvrir_pinces(self):
        self.cs.ax[AX_ID_PINCE_GAUCHE].mode_joint()
        sleep(DELAY)
        self.cs.ax[AX_ID_PINCE_DROITE].mode_joint()
        sleep(0.3)

        self.cs.ax[AX_ID_PINCE_GAUCHE].move(goal=450)
        sleep(DELAY)
        self.cs.ax[AX_ID_PINCE_DROITE].move(goal=550)
        sleep(DELAY)

    @Service.action
    def fermer_pinces(self):
        self.cs.ax[AX_ID_PINCE_GAUCHE].mode_wheel()
        sleep(DELAY)
        self.cs.ax[AX_ID_PINCE_DROITE].mode_wheel()
        sleep(DELAY)

        self.cs.ax[AX_ID_PINCE_GAUCHE].turn(side=False, speed=300)
        sleep(DELAY)
        self.cs.ax[AX_ID_PINCE_DROITE].turn(side=True, speed=300)

    @Service.action
    def ascensseur_bas(self):
        self.cs.ax[AX_ID_ASCENSSEUR].mode_joint()
        sleep(DELAY)
        self.cs.ax[AX_ID_ASCENSSEUR].move(goal=0)

    @Service.action
    def ascensseur_haut(self):
        self.cs.ax[AX_ID_ASCENSSEUR].mode_joint()
        sleep(DELAY)
        self.cs.ax[AX_ID_ASCENSSEUR].move(goal=1023)

    @Service.action
    def avancer(self):
        self.cs.ax[AX_ID_ROUE_GAUCHE].turn(side=False, speed=1023)
        sleep(DELAY)
        self.cs.ax[AX_ID_ROUE_DROITE].turn(side=True, speed=1023)

def main():
    pmi = PMI()
    pmi.run()

if __name__ == '__main__':
    main()
