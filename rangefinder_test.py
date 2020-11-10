#To find centripetal acceleration automatically
"""
Photodiide system:
    +15V and -15V to op amp
    Pi 3.3 V (red)
    Pi 3.3 V
    GPIO 11
    GPIO 9
    GPIO 10
    GPIO 8
    Pi GND
Motor
    Pi 5V
    GPIO 22
    Pi GND
    GPIO 25
    GPIO 24
    Power bank (24V and ground)
Range Finder
    GPIO 16
    Pi Ground
    Analog Ground
    Pi 5V
    GPIO 5
"""
go = 'NO'
while go != 'YES':
    print("Let's find centripetal acceleration! Make sure everything is plugged in, the mass is in place, and the laser is on.")
    go = input("Are you ready? Enter YES or NO (in all caps):")
    
mass = int(input("Please enter the mass in kilograms:"))

#import useful libraries
import spidev
import matplotlib.pyplot as plt
from scipy import signal
import time
import RPi.GPIO as GPIO
import numpy as np
import scipy
from scipy.signal import find_peaks
import pandas as pd
import math

#Set up communication with distance sensor and get initial radius

GPIO.setmode(GPIO.BCM)
trig = 5
echo = 16
GPIO.setup(trig,GPIO.OUT)
GPIO.setup(echo,GPIO.IN)
T_room = 26 #room temperature is 26 C.
print (f'{trig} is the trigger, and {echo} is the echo')
try:
    distlist = []
    
    for i in range(0,10):
        GPIO.output(trig,GPIO.LOW)
        print (f'a 10us pulse is sent to {trig}, ultrasound emitted.')
        time.sleep (0.2) # waiting for 1 second to start
        GPIO.output(trig,GPIO.HIGH)
        time.sleep(0.00001) #supply a 10 us pulse to the trigger input pin to start the ranging
        GPIO.output(trig,GPIO.LOW)
        while GPIO.input(echo) == 0:
            t0 = time.time() #record time now as t0
        while GPIO.input(echo) == 1:
            t1 = time.time() #record the time that the echo pin recvies the reflected sound wave
        t = t1-t0 #calculate the time interval
        v = 20.05* math.sqrt(273.16+T_room)
        d = t*v/2 #calculate the distance in m
        dm = round(d,2)
        dcm = round(100*d, 2)
        din = round(39.37*d,2)
        print (f'The distance is {round(d,2)} m, {round(100*d, 2)}cm, {round(39.37*d,2)}inches.\n')

        distlist.append(dcm)

    davg = sum(distlist)/len(distlist)
    print(davg)
except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()

