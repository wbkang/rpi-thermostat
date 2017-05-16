#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time
import pyowm
import logging
import atexit
import socket
import os

LOCATION = "Toronto,CA"
OWM_API_KEY = os.environ['OWM_API_KEY']

class Weather:

    def __init__(self, location):
        self.owm = pyowm.OWM(OWM_API_KEY)
        self.location = location
    
    def will_rain_today(self):
        return self.owm.daily_forecast(self.location, limit=1).will_have_rain()
    
    def current_temp(self):
        return self.owm.weather_at_place(self.location).get_weather().get_temperature()['temp'] - 273.15


def get_temp_color(t):
    if t < 0:
        return (1, 0, 1) # purple
    if t <= 8:
        return (0, 0, 1) # blue
    if t <= 14:
        return (0, 1, 1) # torq
    if t <= 18:
        return (0, 1, 0) # green
    if t <= 22:
        return (20, 1, 0) # orange
    if t <= 28:
        return (5, 0, 0) # red
    return (50, 1, 1) # pink

class BoardController:
    led_red=16
    led_green=20
    led_blue=21
    led_rain=26
    def __init__(self):
        self.log = logging.getLogger("BoardController")
        GPIO.setmode(GPIO.BCM)
        for c in (\
            BoardController.led_red, BoardController.led_green, BoardController.led_blue,
            BoardController.led_rain):
            GPIO.setup(c, GPIO.OUT)

        self.pwm_red = GPIO.PWM(BoardController.led_red, 60)
        self.pwm_green = GPIO.PWM(BoardController.led_green, 60)
        self.pwm_blue = GPIO.PWM(BoardController.led_blue, 60)
        self.pwm_red.start(0)
        self.pwm_green.start(0)
        self.pwm_blue.start(0)

    def rgb(self, r, g, b):
        self.log.info("RGB:(%d,%d,%d)" % (r, g, b))
        self.pwm_red.ChangeDutyCycle(r)
        self.pwm_green.ChangeDutyCycle(g)
        self.pwm_blue.ChangeDutyCycle(b)
    def rain(self, rain):
        self.log.info("Rain: %s" % rain)
        GPIO.output(BoardController.led_rain, rain)
        

#print("Will rain: %s, temp: %s" % (w.will_rain_today(), w.current_temp()))

def reset_controller():
    logging.getLogger("reset").info("GPIO.cleanup()")
    GPIO.cleanup()

logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s|%(asctime)s|%(name)s] %(message)s')

atexit.register(reset_controller)
bc = BoardController()
w = Weather(LOCATION)

log = logging.getLogger("main")

for t in range(1,35):
    time.sleep(0.5)
    bc.rgb(*get_temp_color(t))


while False:
    try:
        rain = w.will_rain_today()
        temp = w.current_temp()
        log.info("Rain: %s, Temp: %d", rain, temp)
        bc.rgb(*get_temp_color(temp))
        bc.rain(rain)
    except socket.error as ex:
        log.info("Exception while fetching weather")

    log.info("Waiting for 5 minutes")
    time.sleep(300)
