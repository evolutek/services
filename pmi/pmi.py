#!/usr/bin/env python3
from time import sleep

from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service

AX_ID_PINCE_GAUCHE = "1"
AX_ID_PINCE_DROITE = "6"
AX_ID_ASCENSSEUR = "2"

DELTA_PINCES = 40

class PMI(Service):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cs = CellaservProxy(self)

    @Service.action
    def ouvrir_pinces(self):
        self.cs.ax[AX_ID_PINCE_GAUCHE].mode_joint()
        sleep(0.1)
        self.cs.ax[AX_ID_PINCE_DROITE].mode_joint()
        sleep(0.1)

        self.cs.ax[AX_ID_PINCE_GAUCHE].move(goal=460)
        sleep(0.1)
        self.cs.ax[AX_ID_PINCE_DROITE].move(goal=940)
        sleep(0.1)

    @Service.action
    def fermer_pinces(self):
        self.cs.ax[AX_ID_PINCE_GAUCHE].mode_wheel()
        sleep(0.1)
        self.cs.ax[AX_ID_PINCE_DROITE].mode_wheel()
        sleep(0.1)

        self.cs.ax[AX_ID_PINCE_GAUCHE].moving_speed(speed=300)
        sleep(0.1)
        self.cs.ax[AX_ID_PINCE_DROITE].moving_speed(speed=2**10 | 300)

    @Service.action
    def ascensseur_bas(self):
        self.cs.ax[AX_ID_ASCENSSEUR].mode_wheel()
        sleep(0.1)
        self.cs.ax[AX_ID_ASCENSSEUR].moving_speed(speed=2**10 | 1000)
        sleep(1)
        self.cs.ax[AX_ID_ASCENSSEUR].moving_speed(speed=0)

    @Service.action
    def ascensseur_haut(self):
        self.cs.ax[AX_ID_ASCENSSEUR].mode_wheel()
        sleep(0.1)
        self.cs.ax[AX_ID_ASCENSSEUR].moving_speed(speed=1000)
        sleep(1)
        self.cs.ax[AX_ID_ASCENSSEUR].moving_speed(speed=0)


def main():
    pmi = PMI()
    pmi.run()

if __name__ == '__main__':
    main()
