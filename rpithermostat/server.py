#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time
import threading
import logging
from tzlocal import get_localzone
from flask import Flask, render_template, url_for, request
from rpithermostat import outside_weather
from rpithermostat import sampler
from rpithermostat import temphumids
from rpithermostat import display 
from rpithermostat import sampler
from rpithermostat import oracle 
from rpithermostat import collector 
from rpithermostat import controller 
import datetime
import json


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(message)s')
GPIO.setmode(GPIO.BCM)
logger = logging.getLogger(__name__)


app = Flask("rpithermostat")


def format_timestamps(series):
    local_tz = get_localzone()
    return list(
        str(dt.tz_localize("UTC").tz_convert(local_tz)) for dt in series
    )


@app.route("/")
def index():
    th = temphumids.get_current_temphumid()
    target = oracle.get_target_temperature()
    return render_template("index.html",
                           temperature=th['temperature'],
                           humidity=th['humidity'],
                           target_temp=target)

@app.route("/temperature/up", methods=["POST"])
def temp_up():
    t = oracle.get_target_temperature()
    oracle.set_target_temperature(t + 1)
    controller.temp_manager()
    return ""

@app.route("/temperature/down", methods=["POST"])
def temp_down():
    t = oracle.get_target_temperature()
    oracle.set_target_temperature(t - 1)
    controller.temp_manager()
    return ""

@app.route("/feeling/too_cold", methods=["POST"])
def too_cold():
    collector.record_reaction(-1)
    return ""

@app.route("/feeling/too_hot", methods=["POST"])
def too_hot():
    collector.record_reaction(1)
    return ""

@app.route("/feeling/happy", methods=["POST"])
def happy():
    collector.record_reaction(0)
    return ""

@app.route("/status")
def status():
    t = oracle.get_target_temperature()
    target_humidity = oracle.get_target_humidity()
    th = temphumids.get_current_temphumid()
    state = oracle.get_governor().hb_num

    status = {'targetHeatingCoolingState':state,
              'targetTemperature':t,
              'targetRelativeHumidity':target_humidity,
              'currentHeadingCoolingState':state,
              'currentTemperature':th['temperature'],
              'currentRelativeHumidity':th['humidity']
              }

    return json.dumps(status)

@app.route("/targetTemperature/<temp>")
def set_target_temp(temp):
    oracle.set_target_temperature(float(temp))
    return ""

@app.route("/targetRelativeHumidity/<rh>")
def set_rh(rh):
    oracle.set_target_humidity(float(rh))
    return ""


@app.route("/off")
def set_status_off():
    oracle.set_governor("off")
    return ""

@app.route("/comfort")
def set_status_heat():
    oracle.set_governor("heat")
    return ""

@app.route("/no-frost")
def set_status_cool():
    oracle.set_governor("cool")
    return ""

temphumids.start_recording()
outside_weather.start_recording()
oracle.start()
display.start_display()

logger.info("Started")
logger.info("Outside temp is %r" % outside_weather.get_recent_temp())
