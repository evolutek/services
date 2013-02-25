#!/usr/bin/env python3
from time import sleep
from cellaserv.proxy import CellaservProxy

def lift(cs):
    cs.pmi.lacher_pinces()
    sleep(.2)
    cs.pmi.ascenseur_bas()
    sleep(1)
    cs.pmi.fermer_pinces()
    sleep(.1)
    cs.pmi.ascenseur_haut()
    sleep(2)

def hold(cs):
    cs.pmi.lacher_pinces()
    sleep(.5)
    cs.ax["2"].move(goal=300)
    sleep(.5)
    cs.pmi.fermer_pinces()
    sleep(.5)
    cs.ax["2"].move(goal=400)

def forward(cs):
    cs.pmi.vitesse(speed=1023)
    sleep(1)
    cs.pmi.vitesse(speed=0)

def main():
    cs = CellaservProxy()
    cs.pmi.ouvrir_pinces()
    sleep(.4)
    for i in range(3):
        #forward(cs)
        lift(cs)
    #forward(cs)
    hold(cs)

if __name__ == '__main__':
    main()
