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

#Set up motor
GPIO.setmode(GPIO.BCM)
GPIO.setup(25,GPIO.OUT)
GPIO.setup(22,GPIO.OUT)
GPIO.setup(24,GPIO.OUT)
print("Motor is all set to go!")
forward = GPIO.PWM(25,100)
reverse = GPIO.PWM(22,100)


#Drive motor
forward.start(0)              #start with forward spin
reverse.start(0)


print("Run Motor")
GPIO.output(24,GPIO.HIGH)     #Tells the motor its go time
speed = input("Input FAST, MEDIUM, or SLOW to get a spinning speed:")
if speed == 'SLOW':
    forward.ChangeDutyCycle(33.3)  #Forward spin speed (0%-100% Duty Cycle)
    reverse.ChangeDutyCycle(0)    #Reverse spin speed (0%-100% Duty Cycle)
                                  #Note:  if Forward is not zero, Reverse should be zero and vice versa
    time.sleep(5)                      #5 seconds to get smooth, constant speed
elif speed == 'MEDIUM':
    forward.ChangeDutyCycle(66.7)
    reverse.ChangeDutyCycle(0)

    time.sleep(5)
elif speed == 'FAST':
    forward.ChangeDutyCycle(100)
    reverse.ChangeDutyCycle(0)

    time.sleep(5)
else:
    print("Not a valid command, try again.")

print("Now Stop")
GPIO.output(24,GPIO.LOW)      #Tells the motor its time to stop
forward.stop()
reverse.stop()

GPIO.cleanup()
