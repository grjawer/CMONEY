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
#import useful libraries
import spidev
import matplotlib.pyplot as plt
from scipy import signal
import time
import RPi.GPIO as GPIO
import numpy as np
import scipy
from scipy.signal import find_peaks
import math
import csv

def read_adc(channel):
    if not 0 <= channel <= 7:
        raise IndexError('Invalid. enter 0, 1, ..., 7' )
    """datasheep page 19 about setting sgl/diff bit to high, hence we add 8 = 0b1000
    left shift 4 bits to make space for the second byte of data[1]"""
    request = [0x1, (8+channel) << 4, 0x0] # [start bit, configuration, listen space] 
    data = spi.xfer2(request) #data is recorded 3 bytes: data[0] - throw away, data[1] - keep last 2 bits, data[2] - keep all
    data10bit = ((data[1] & 3) << 8) + data[2] #shfit bits to get the 10 bit data
    return data10bit

def Find_cforce():  #Gets centripetal force from user input of given mass and set speed. Returns mass, radius, angular velocity, and centripetal forc

    mass = int(input("Please enter the mass in kilograms:"))

    #Set up communication with photodiode circuit
    spi = spidev.SpiDev() #open spi bus
    spi.open(0,0) #open(bus, device)
    spi.max_speed_hz=1000000
    spi.mode = 0b00 #spi modes; 00,01,10,11
    print("Photodiode output is now set up.")

    #Set up communication with distance sensor and get initial radius
    GPIO.setmode(GPIO.BCM)
    trig = 5
    echo = 16
    GPIO.setup(trig,GPIO.OUT)
    GPIO.setup(echo,GPIO.IN)
    T_room = 26 #room temperature is 26 C.
    print('Getting radius...')
    #print (f'{trig} is the trigger, and {echo} is the echo')
    try:
        distlist = []

        for i in range(0,50):
            GPIO.output(trig,GPIO.LOW)
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
            #print (f'The distance is {round(d,2)} m, {round(100*d, 2)}cm, {round(39.37*d,2)}inches.\n')

            distlist.append(dm)

        davg = sum(distlist)/len(distlist)
        #print(davg)
    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup()

    distance = 0.375
    radius = distance - davg    #radius is distance from shaft to mass = (total distance from sensor to shaft) - (distance from sensor to mass)
    print('Radius is ', radius, 'meters')

    #Set up motor
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(25,GPIO.OUT)
    GPIO.setup(22,GPIO.OUT)
    GPIO.setup(24,GPIO.OUT)
    print("Motor is all set to go!")
    forward = GPIO.PWM(25,100)
    reverse = GPIO.PWM(22,100)

    #Drive motor
    forward.start(0)              #start with no spin
    reverse.start(0)

    print("Run Motor")
    GPIO.output(24,GPIO.HIGH)     #Tells the motor its go time
    speed = input("Input FAST, MEDIUM, or SLOW to get a spinning speed:")
    if speed == 'SLOW':
        forward.ChangeDutyCycle(33.3)  #Forward spin speed (0%-100% Duty Cycle)
        reverse.ChangeDutyCycle(0)    #Reverse spin speed (0%-100% Duty Cycle)
                                      #Note:  if Forward is not zero, Reverse should be zero and vice versa
        time.sleep(.5)                      #5 seconds to get smooth, constant speed
    elif speed == 'MEDIUM':
        forward.ChangeDutyCycle(66.7)
        reverse.ChangeDutyCycle(0)

        time.sleep(.5)
    elif speed == 'FAST':
        forward.ChangeDutyCycle(100)
        reverse.ChangeDutyCycle(0)

        time.sleep(.5)
    else:
        print("Not a valid command, try again.")

    #Gather data for frequency
    volt = []
    print("Getting data now... press Ctrl + c when done")
    t0 = time.time()            #inital time
    for i in range(10):         #spin for about 10 seconds
            v_volt = read_adc(1) * 3.3 / 1024   #get voltage from photodiode circuit input to channel 1
            volt.append(v_volt)                 #add voltage to list
            time.sleep(1)
    tf = time.time()            #final time

    print("Now Stop")
    GPIO.output(24,GPIO.LOW)      #Tells the motor its time to stop
    forward.stop()
    reverse.stop()

    GPIO.cleanup()

    #Calculate centripetal force
    peaks, _ = find_peaks(volt, height=0.35, distance = 2000)   #light is hitting sensor if voltage>0.35, with more than 2000 units between peaks
    rotations = len(peaks)      #number of peaks = number of rotations
    t_total = tf - t0           #total time for rotations
    print('Total time was', t_total, 'seconds')
    print('And', rotations, 'rotations.')
    frequency = rotations / t_total         #frequency!
    print('Frequency was ', frequency, 'rotations per second')
    omega = 2 * np.pi * frequency           #angular velocity!
    print('Angular velocity was ', omega, 'radians per second')
    alpha = radius * omega                  #angular acceleration
    print('Angular acceleration was ', alpha, 'radians per second squared')
    force = mass * radius * omega**2         #CENTRIPETAL FORCE!
    print('Centripetal force is:', force, 'Newtons!')

    #plt.plot(volt) 
    #plt.show()

    return mass, radius, omega, force

go = 'NO'
while go != 'YES':
    print("Let's find centripetal acceleration! Make sure everything is plugged in, the mass is in place, and the laser is on.")
    go = input("Are you ready? Enter YES or NO (in all caps):")

Masses = []  
Radii = []
Omegas = []
Forces = []

Mass, Radius, Omega, Force = Find_cforce()

Masses.append(Mass)
Radii.append(Radius)
Omegas.append(Omega)
Forces.append(Force)

again = 'YES'
while again == 'YES':
    again = input("Would you like to try again with a different mass or different speed? Enter YES or NO (in all caps):")
    if again == 'NO':
        pass
    Mass1, Radius1, Omega1, Force1 = Find_cforce()
    Masses.append(Mass1)
    Radii.append(Radius1)
    Omegas.append(Omega1)
    Forces.append(Force1)

# write to csv:
filename = '/home/pi/Desktop/' + str(time.time()) + '.csv'
with open(filename, ’w’, newline=’’) as csvfile:
    writer = csv.writer(csvfile, delimiter=’ ’, quotechar=’|’, quoting=csv.QUOTE_MINIMAL)
    writer.writerow(Masses)
    writer.writerow(Radii)
    writer.writerow(Omegas)
    writer.writerow(Forces)
    
print('Thank you for using CMONEY! Your data is available as a csv file on the Pi desktop.')    
