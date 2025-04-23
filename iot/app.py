from flask import Flask, request, render_template, Response
#from flask_cors import CORS

from gpiozero import LED, Button, DistanceSensor
import sensor
import gate
import post_data
import time
import threading

sleep=1

led = LED(4)
button = Button(18)
#distance = DistanceSensor(24,23)
sensor = sensor.Sensor()
gate = gate.Gate()

app = Flask(__name__)

@app.route('/')
def helloworld():
    return "Hello World!"

@app.route('/led')
def led_on():
    state = request.args.get("state")
    if state == "on":
        led.on()
    else:
        led.off()
    return 'LED' + state

def button_pressed():
    print("Button Pressed")

def t1_main():
   # button.when_pressed = button_pressed
    distances = DistanceSensor(24,23)
    while True:
        distance = distances.distance
        print(distance)
        if(distance < 10):
            htdata = sensor.read_temperature()
            print(htdata)
            gate.open()
#           led.fadein()
            post_data.http_post_data(htdata)
        else:
            gate.close()
#           led.off()              
        time.sleep(3)

if __name__ == '__main__':
    t1 = threading.Thread(target=t1_main)
    t1.start()
    app.run('0.0.0.0',port=5000, debug=False, threaded=True)