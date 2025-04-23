import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

TRIG=23
ECHO=24

GPIO.setup(TRIG,GPIO.OUT)
GPIO.setup(ECHO,GPIO.IN)
stop = 0
start = 0

def distance_measure():
    GPIO.output(TRIG,True)
    time.sleep(0.00001)
    GPIO.output(TRIG,False)
    while GPIO.input(ECHO)==0:
        start=time.time()
    while GPIO.input(ECHO)==1:
        stop=time.time()
    check_time=stop-start
    distance=check_time*34300/2
    return(distance)

import Adafruit_DHT
sensor = Adafruit_DHT.DHT11

pin=2

def temphumidity_measure():
    humidity, temperature = Adafruit_DHT.read_retry(sensor,pin)
    print('Temp={0:0.1f}*C Humidity={1:0.1f}%'.format(temperature,humidity))
    return temperature,humidity