#!/usr/bin/env python3
import time

from cellaserv.proxy import CellaservProxy

def main():
    cs = CellservProxy()

    while True:
        cs.pmi.ascensseur_haut()
        time.sleep(2)
        cs.pmi.ascensseur_bas()
        time.sleep(2)

if __name__ == '__main__':
    main()
