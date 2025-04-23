
from flask import Flask, request, render_template, Response
from flask_cors import CORS

import RPi.GPIO as GPIO
import sensor, actuator
import time
import post_data
import servo
import threading
import motion_cv

sleep=1

app = Flask(__name__)
CORS(app)

@app.route('/')
def helloworld():
    return "Hello World!"

@app.route('/cv_motion')
def cv_motion():
    # rendering webpage
    return render_template('cv_motion.html')
	
@app.route('/video_feed')
def video_feed():
    return Response(motion_cv.gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/led')
def led_on():
    state = request.args.get("state")
    if state == "on":
        actuator.LED_control(actuator.ON)
    else:
        actuator.LED_control(actuator.OFF)
    return 'LED' + state

def t1_main():
    while True:
        distance = sensor.distance_measure()
        if(distance < 10):
            htdata = sensor.temphumidity_measure()
            print(htdata)
            servo.set_servo_degree(90)
#            actuator.LED_control(1)
            post_data.http_post_data(htdata)
        else:
            servo.set_servo_degree(0)
#            actuator.LED_control(0)              
        time.sleep(1)

if __name__ == '__main__':
    t1 = threading.Thread(target=t1_main)
    t1.start()
    app.run('0.0.0.0',port=5000, debug=False, threaded=True)