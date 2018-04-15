import RPi.GPIO as GPIO
import os
import time
from decimal import Decimal
import math

print("Preparing to monitor sound levels")
print("You can gracefully exit the program by pressing ctrl-C")
print("Readying Web Output File")

web_file = "/var/www/html/table.shtml"
with open(web_file + '.new', 'w') as f_output:
    f_output.write("")
    os.rename(web_file + '.new', web_file)

Loud_Count = 0 #global upper-case
louds_per = 0
per_detected = 0
time_loop = 5
stime = time.time()
etime = stime + time_loop
ptime = time.ctime()
Loops_Tot = 0
loop_count = 0
max_loop = 10000000
a_threshold = .00000001
sensor_in = 18
red_led = 21
green_led = 20

GPIO.setmode(GPIO.BCM)
GPIO.setup(red_led, GPIO.OUT)
GPIO.setup(green_led, GPIO.OUT)
GPIO.setup(sensor_in, GPIO.IN)
GPIO.output(green_led, GPIO.LOW)
GPIO.output(red_led, GPIO.LOW)
GPIO.output(green_led, GPIO.HIGH)
print("GPIO set. Service ready. Initiating Detection Protocol.")
GPIO.add_event_detect(sensor_in, GPIO.RISING, bouncetime = 300)

def dowork(sensor_in):
    global Loud_Count, loop_count, per_detected, max_loop, louds_per
    if GPIO.input(sensor_in):
        GPIO.output(red_led, GPIO.HIGH)
        Loud_Count = Loud_Count + 1
        louds_per = louds_per + 1
        per_detected = Decimal(louds_per)/Decimal(loop_count)
        per_detected = round(per_detected, 10)
        if per_detected > a_threshold:
            print("REALLY PRETTY LOUD! Detect vs Threshold:" + str(per_detected) + " / " + str(a_threshold))
            print(str(loop_count) + "loops vs" + str(louds_per) + "events")
        else:
            print("Meh. Some noise. Detect vs Threshold: " + str(per_detected) + " / " + str(a_threshold))
            print(str(loop_count) + "loops vs" + str(louds_per) + "events")
try:
    etime = time.time() + time_loop
    while(True):
        loop_count = loop_count + 1
        Loop_Tot = Loops_Tot + 1
        if GPIO.event_detected(sensor_in):
            dowork(sensor_in)
            GPIO.remove_event_detect(sensor_in)
            time.sleep(0.25)
            GPIO.add_event_detect(sensor_in, GPIO.RISING, bouncetime = 300)
        if time.time() > etime:
            with open(web_file, 'a') as f_output:
                if louds_per > 5:
                    if louds_per > 10:
                        f_output.write("<tr><td align=center bgcolor=red   ><font color=write>On" + str(ptime) + ", it was Loud!!!</td><td align=center bgcolor=red><font color=white>"+str(louds_per)+"</font></td></tr>")
                    else:
                        f_output.write("<tr><td align=center bgcolor=orange><font color=write>On" +str(ptime) + ", it was a little Loud!!!</td><td align=centerbgcolor=orange><font color=white>" + str(louds_per) + "</font></td></tr>")
                    else:
                        f_output.write("<tr><td align=center bgcolor=green ><font color=write>On" + str(ptime) + ", it was pretty quite!!!</td><td align=center bgcolor=green><font color=white>" + str(louds_per) + "</font></td></tr>")
        print("Resetting Counters")
        loop_count = 0
        louds_per = 0
        etime = time.time() + time_loop
        ptime = time.ctime(etime)
        GPIO.output(red_led, GPIO.LOW)
except (KeyboardInterrupt, SystemExit):
    print("-----------------------")
    print(" ")
    print("System reset on keyboard command or sysexit")
    print(" ")
    print("total noises detected: "+str(Loud_Count))
    print(" ")
    print("total loops run:" + str(Loops_Tot))
    print(" ")
    print("-----------------------")
    GPIO.cleanup()
else:
    print("-----------------------")
    print(" ")
    print("System reset for some reason")
    print(" ")
    print("total noises detected: "+str(Loud_Count))
    print(" ")
    print("total loops run:" + str(Loops_Tot))
    print(" ")
    print("-----------------------")
    GPIO.cleanup()
#green_led = 20
#GPIO.setmode(GPIO.BCM)
#GPIO.setup(green_led, GPIO.OUT)
#GPIO.output(green_led, GPIO.HIGH)
#time.sleep(5)
#GPIO.output(green_led, GPIO.LOW)
#print("rock the kazbah")
