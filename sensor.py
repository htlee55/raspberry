import smbus
import time
import math

bus = smbus.SMBus(1)
add = 0x48                          #PCF8591T I2C 주소값
CDS_AIN0 = 0x40                     #cds, 광량에 따라 저항이 변하는 특성
THERM_AIN1 = 0x41                   #THermister, 온도에 따라 저항이 변하는 특성
POTEN_AIN3 = 0x43                   #variable resister

def read_adc(channel):
    try:
        bus.write_byte(add,channel)
        bus.read_byte(add)          #dummy read to start conversion( 8bit AD Coversion)
        time.sleep(0.1)
        return bus.read_byte(add)
    except Exception as e:
        print(f"I2C Error: {e}")
        return 0

def read_lux():
    raw = read_adc(CDS_AIN0)
    #Vcds = raw / 256 * 3.3          #AIN0 전압값 (전원: 3.3V), 8bit voltage data
    R_fixed = 1000                  #1 KOhm 고정 저항
    try:
        R_cds = (raw * R_fixed)/(256 - raw)
        print(f"CDS resistance: {round(R_cds,2)}")
    except ZeroDivisionError:
        R_cds = float('inf')
    if R_cds !=0:
    #    lux = 500000 / R_cds        #(R_cds = 500/lux (KOhms))로 가정
    #감마값(0.6)으로부터 계산하는 방법
        lux = math.pow((50000/R_cds),1/0.6)
    else:
        lux = 500
    return round(lux,2)

def read_temperature():
    raw = read_adc(THERM_AIN1)
    #Vtherm = raw / 256 * 3.3            #AIN1 전압값 (전원: 3.3V), 8bit voltage data
    R_fixed = 1000                      #1 KOhm 고정 저항
    beta = 3950
    T0 = 25.0
    R_therm = (raw * R_fixed)/(256 - raw)     #써미스터 저항
    steinhart = math.log(R_therm/10000) / beta       
    steinhart += 1.0 / (T0 + 273.15)
    steinhart = (1.0 / steinhart) - 273.15
    return round(steinhart,2)

def read_potentiometer():
    raw = read_adc(POTEN_AIN3)
    Vpotentio = raw / 255 * 3.3            #AIN3 전압값 (전원: 3.3V), 8bit voltage data
    return round(Vpotentio,2)