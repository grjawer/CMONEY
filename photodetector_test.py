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

#Set up communication with photodiode circuit
spi = spidev.SpiDev() #open spi bus
spi.open(0,0) #open(bus, device)
spi.max_speed_hz=1000000
spi.mode = 0b00 #spi modes; 00,01,10,11
print("Photodiode output is now set up.")

def read_adc(channel):
    if not 0 <= channel <= 7:
        raise IndexError('Invalid. enter 0, 1, ..., 7' )
    """datasheep page 19 about setting sgl/diff bit to high, hence we add 8 = 0b1000
    left shift 4 bits to make space for the second byte of data[1]"""
    request = [0x1, (8+channel) << 4, 0x0] # [start bit, configuration, listen space] 
    data = spi.xfer2(request) #data is recorded 3 bytes: data[0] - throw away, data[1] - keep last 2 bits, data[2] - keep all
    data10bit = ((data[1] & 3) << 8) + data[2] #shfit bits to get the 10 bit data
    return data10bit


#Gather data for frequency
volt = []
print("Getting data now... press Ctrl + c when done")
t0 = time.time()            #inital time
try:
    while 1:
        v_volt = read_adc(1) * 3.3 / 1024   #get voltage from photodiode circuit
        volt.append(v_volt)                 #add voltage to list, light is hitting sensor if voltage>3
except KeyboardInterrupt:
    pass
tf = time.time()            #final time

#Calculate centripetal force
plt.plot(volt)
plt.show()

peaks, _ = find_peaks(volt, height=0.35, distance = 5000)
rotations = len(peaks)
t_total = tf - t0
print('Total time was', t_total, 'seconds')
print(rotations, 'rotations')
frequency = rotations / t_total         #frequency!
print('Frequency was ', frequency, 'rotations per second')
omega = 2 * np.pi * frequency           #angular velocity!
