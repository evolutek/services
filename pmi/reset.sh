#! /bin/bash

killall pmi.py

cellaquery -s 192.168.1.168 apmi.move s=0
cellaquery -s 192.168.1.168 apmi.pliers a=\"open\"
