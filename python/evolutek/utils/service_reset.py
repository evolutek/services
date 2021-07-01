from os import system
from time import sleep
import RPi.GPIO as GPIO

RESET_GPIO = 40

def restartAll():
    print("let's fucking go for a reset lmao")
    system("sudo systemctl restart trajman")
    system("sudo systemctl restart actuators")
    system("sudo systemctl restart robot")
    system("sudo systemctl restart ai")

def main():

    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(RESET_GPIO, GPIO.IN)
    triggered = False
    needRestart = False
    lastVal = GPIO.HIGH
    while True:
        val = GPIO.input(RESET_GPIO)
        if val == GPIO.LOW and lastVal == GPIO.HIGH:
            needRestart = True
        elif val == GPIO.HIGH:
            needRestart = False
        if needRestart:
            restartAll()
            needRestart = False
        lastVal = val

        sleep(0.5)



if __name__ == '__main__':
    main()
