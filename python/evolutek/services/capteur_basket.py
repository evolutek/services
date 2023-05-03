import RPi.GPIO as GPIO # importe la bibliothèque RPi.GPIO pour accéder aux entrées et sorties du GPIO de la Raspberry Pi.
import time

GPIO.setmode(GPIO.BCM) # mode d'adressage des broches GPIO. C'est le mode d'adressage que vous devez utiliser lorsque vous programmez en Python.
GPIO.setup(4, GPIO.IN) #configure la broche GPIO 4 en mode d'entrée.

counter = 0 #global

def count_ball():
    try:
        while True:
            if GPIO.input(4) == 1: #si le capteur renvoie 1
                counter += 1
                print("Capteur actif, compteur incrémenté à", counter)
            else:
                print("Capteur inactif")
            time.sleep(1)

    except KeyboardInterrupt: # CTRL + C pour interrompre le script.
        GPIO.cleanup() #nettoie GPIO en cas d'interruption du script.
