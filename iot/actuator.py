import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
LED = 4
ON = 1
OFF = 0
GPIO.setup(LED,GPIO.OUT, initial= GPIO.LOW)

def LED_control(command):
    if command==ON:
        GPIO.output(LED,True)
    else:
        GPIO.output(LED,False)