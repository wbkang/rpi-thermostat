#!/usr/bin/env python

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

led_red = 16
led_green = 20
GPIO.setup(led_red, GPIO.OUT)
GPIO.setup(led_green, GPIO.OUT)

#time.sleep(5)

#GPIO.setup(21, GPIO.IN)

pwm_red = GPIO.PWM(led_red, 10000)
pwm_green = GPIO.PWM(led_green, 10000)

pwm_red.start(0)
pwm_green.start(0)

for p in pwm_red, pwm_green:
    for b in xrange(0, 100):
        p.ChangeDutyCycle(b)
        print b
        time.sleep(0.1)
    p.ChangeDutyCycle(0)


if False:
    pwm = GPIO.PWM(21, 10000)
    pwm.start(0)

    for b in xrange(0, 100):
        pwm.ChangeDutyCycle(b)
        time.sleep(0.1)

GPIO.cleanup()
