from os import system
from time import sleep, time
import RPi.GPIO as GPIO

RESET_GPIO = 21
POWER_HOLD = 5
POWER_INT = 6

def restartAll(channel):
    print("Restart all services")
    system("sudo systemctl restart config")
    system("sudo systemctl restart match")
    system("sudo systemctl restart trajman")
    system("sudo systemctl restart actuators")
    system("sudo systemctl restart robot")
    system("sudo systemctl restart ai")
    #system("sudo systemctl restart cellaserv")

def shutDown(channel):
    print("Shutdown requested")
    #print("Turning off robot")
    #GPIO.output(POWER_HOLD, GPIO.LOW)
    #system("sudo poweroff")

def init():
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(RESET_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    #GPIO.add_event_detect(RESET_GPIO, GPIO.RISING, callback=restartAll, bouncetime=1000)

    GPIO.setup(POWER_HOLD, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(POWER_INT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    #GPIO.add_event_detect(POWER_INT, GPIO.FALLING, callback=shutDown, bouncetime=1000)

    system("sudo systemctl restart cellaserv")

def main():

    print("Service Reset starting")
    init()
    print("Init complete")
    last_print_time = time()
    reset_last_val = GPIO.LOW
    needRestart = False
    power_int_last_val = GPIO.HIGH
    needShutDown = False
    while True:
        if time() - last_print_time > 2.0:
            print("Still running")
            last_print_time = time()

        reset_val = GPIO.input(RESET_GPIO)
        if reset_val == GPIO.HIGH and reset_last_val == GPIO.LOW:
            needRestart = True
        elif reset_val == GPIO.LOW:
            needRestart = False
        if needRestart:
            restartAll(0)
            needRestart = False
        reset_last_val = reset_val

        power_int_val = GPIO.input(POWER_INT)
        if power_int_val == GPIO.HIGH and power_int_last_val == GPIO.LOW:
            needShutDown = True
        elif power_int_val == GPIO.LOW:
            needShutDown = False
        if needShutDown:
            shutDown(0)
            needShutDown = False
        power_int_last_val = power_int_val

        sleep(0.1)


if __name__ == '__main__':
    main()
