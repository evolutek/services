from cellaserv.proxy import CellaservProxy
from cellaserv.service import AsynClient
from cellaserv.settings import get_socket
from json import dumps
from random import randint

RUN = 50
ROBOT = 'pal'

def test():
    cs = CellaservProxy()
    client = AsynClient(get_socket())

    i = 1

    while i <= RUN:

        print('Running test %d' % i)

        print('Resetting match')
        cs.match.reset_match()

        strat = randinr(1, 3)
        print('Going with startegy %d' % strat)
        cs.ai[ROBOT].set_strategy(index=strat)

        print('Recalibrating robot')
        cs.ai[ROBOT].reset(recalibrate_itself=True)

        print('Press Enter to launch test %d' % i)
        input()

        data = dumps({}).encode()
        client.publish('tirette', data=data)

        status = 'Unknow'
        while status != 'Ended':
            status = cs.match.get_status()['status']
        
        print('Test %d ended' % i)
        print('Please setup again the table then press Enter')
        input()

        i += 1

        