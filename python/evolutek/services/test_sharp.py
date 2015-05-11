from time import sleep
import mraa
from evolutek.lib.settings import ROBOT

while True:
    print(' ')
    print('0', mraa.Aio(0).readFloat())
    print('1', mraa.Aio(1).readFloat())
    print('2', mraa.Aio(2).readFloat())
    print('3', mraa.Aio(3).readFloat())
    sleep(1)
