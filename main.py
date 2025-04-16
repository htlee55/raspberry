import time
from sensor_class import Sensor

def main():
    sensor = Sensor()
    while True:
        print(f"illuminance:{sensor.read_lux()}")
        print(f"Temperature:{sensor.read_temperature()}")
        print(f"Potentiometer:{sensor.read_potentiometer()}")
        time.sleep(1)

if __name__ == "__main__":
    main()