#!/usr/bin/env python

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

buzz = 6

GPIO.setup(buzz, GPIO.OUT)

GPIO.output(buzz, False)

pwm = GPIO.PWM(buzz, 10)
pwm.start(50)

time.sleep(2)
GPIO.output(buzz, False)
GPIO.cleanup()
