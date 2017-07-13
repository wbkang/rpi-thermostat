#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time
import threading
from threading import Lock
import logging
from tzlocal import get_localzone
from flask import Flask, render_template, url_for, request
from rpithermostat import sampler
import Adafruit_CharLCD as LCD
from collections import deque
from functools import reduce
import datetime

lock_temphumids = Lock()
temphumids = deque([], maxlen=30)
status_message = ""


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(message)s')
GPIO.setmode(GPIO.BCM)
logger = logging.getLogger(__name__)


app = Flask("rpiweather")


def format_timestamps(series):
    local_tz = get_localzone()
    return list(
        str(dt.tz_localize("UTC").tz_convert(local_tz)) for dt in series
    )


@app.route("/")
def index():
    return render_template("index.html")


from dht11 import dht11

temp_humid = dht11.DHT11(26)

pin_heat = 16
pin_fan = 21
pin_cooling = 20
for pin in [pin_heat, pin_fan, pin_cooling]:
    GPIO.setup(pin, GPIO.OUT)

def heat(onoff):
    GPIO.output(pin_heat, onoff)
def fan(onoff):
    GPIO.output(pin_fan, onoff)
def cooling(onoff):
    GPIO.output(pin_cooling, onoff)

lcd_rs        = 14 
lcd_en        = 15
lcd_d4        = 18
lcd_d5        = 23 
lcd_d6        = 24 
lcd_d7        = 25 
lcd_backlight = 19

# Define LCD column and row size for 16x2 LCD.
lcd_columns = 16
lcd_rows    = 2

# Initialize the LCD using the pins above.
lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7,
                           lcd_columns, lcd_rows, lcd_backlight, invert_polarity=False, enable_pwm=True)

lcd.set_backlight(1)

def get_current_temphumid():
    with lock_temphumids:
        size = len(temphumids)
        avg_t = reduce(lambda tally, b: tally + b.temperature, temphumids, 0) / size
        avg_h = reduce(lambda tally, b: tally + b.humidity, temphumids, 0) / size
        return {'temperature':avg_t, 'humidity':avg_h}

def record_temp():
    current = temp_humid.read()
    if current.is_valid():
        with lock_temphumids:
            temphumids.append(current)
    else:
        # retrying
        record_temp()

record_temp()
measure_thread = sampler.Sampler(1, record_temp)
measure_thread.start()

def display():
    target_temp = get_target_temperature()
    current = get_current_temphumid()
    current_temp = current['temperature']
    current_humidity = current['humidity']
    
    lcd.clear()
    lcd.show_cursor(True)
    lcd.blink(True)
    lcd.message("%dC @ %d%% -> %dC\n%s" % (current_temp, current_humidity, target_temp, status_message))

display_thread = sampler.Sampler(1, display)
display_thread.start()

def is_night():
    dt = datetime.datetime.now()
    return not (dt.hour >= 8 and dt.hour < 22)

def get_target_temperature():
    dt = datetime.datetime.now()
    return 25 if not is_night() else 27

def temp_manager():
    global status_message
    target_temp = get_target_temperature()
    current = get_current_temphumid()
    current_temp = current['temperature']
    current_humidity = current['humidity']
    target_humidity = 40
    logger.info("Current temperature: %d, Target: %d" % (current_temp, target_temp))
    
    if current_temp >= target_temp or (not is_night() and current_humidity >= target_humidity ):
        logger.info("Too hot! Start cooling")
        fan(True)
        heat(False)
        cooling(True)
        status_message = "Cooling"
    elif abs(current_temp - target_temp) < 1:
        logger.info("Temp difference minimal, stop")
        fan(True)
        heat(False)
        cooling(False)
        status_message = "Idle"
    elif current_temp >= target_temp:
        logger.info("Too hot! Start cooling")
        fan(True)
        heat(False)
        cooling(True)
        status_message = "Cooling"
    else:
        logger.info("Too cold! Idling")
        fan(True)
        heat(False)
        cooling(False)
        status_message = "Idle"




temp_thread = sampler.Sampler(30, temp_manager)
temp_thread.start()

logger.info("Started")
while True:
    time.sleep(1)
