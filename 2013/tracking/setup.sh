#! /bin/bash

echo 'For more information, see http://doc.evolutek.org/services/hokuyo.html'

cellaquery hokuyo[beacon2].set-position pos=2
cellaquery hokuyo[beacon2].add-deadzone type=circle x=1500 y=2000 radius=500
#cellaquery hokuyo[beacon2].set-position pos=2
#cellaquery hokuyo[beacon2].add-deadzone type=circle x=1500 y=2000 radius=500
