#!/usr/bin/env python

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

trigger = 25
echo = 12


GPIO.setup(trigger, GPIO.OUT)
GPIO.setup(echo, GPIO.IN)

while True:
    GPIO.output(trigger, False)
    print("Waiting for trigger to settle")

    time.sleep(1)

    GPIO.output(trigger, True)
    time.sleep(0.00001)
    GPIO.output(trigger, False)

    pulse_start = -1
    ch = GPIO.wait_for_edge(echo, GPIO.RISING, timeout=1000)
    if not ch:
        print("time out for up")
        continue
    pulse_start = time.time()
    ch = GPIO.wait_for_edge(echo, GPIO.FALLING, timeout=1000)
    if not ch:
        print("time out for down")
        continue
    pulse_end = time.time()

    duration = pulse_end - pulse_start
    print("duration:%s" % duration)

    distance = duration * 1000000 / 58

    print("distance is %dcm" % distance)


GPIO.cleanup()
