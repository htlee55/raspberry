from flask import Flask
import os
#os.environ['GPIOZERO_PIN_FACTORY'] = os.environ.get('GPIOZERO_PIN_FACTORY', 'mock')
import gpiozero
from signal import pause
from gpiozero.pins.native import NativeFactory

led = gpiozero.LED(4)
app = Flask(__name__)

debug = False
@app.route('/')
def home():
    return 'This is Home!'

@app.route('/led/on')
def led_on():
    led.on()
    return 'LED_ON'

@app.route('/led/off')
def led_off():
    led.off()
    return 'LED_OFF'

if __name__ == '__main__':
    if debug:
        gpiozero.Device.pin_factory = NativeFactory()
    app.run('0.0.0.0', port=5000, debug=False)