from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory

class Gate:
    def __init__(self,gpio_no=18):
        self.factory = PiGPIOFactory()
        self.servo = Servo(18, pin_factory=PiGPIOFactory(),
            min_pulse_width=0.544/1000, # Adjust if needed
            max_pulse_width=2.4/1000, # Adjust if needed
        )
    def open(self):
        self.servo.value = 1

    def close(self):
        self.servo.value = -1