import pyowm
import os
from .sampler import Sampler
import datetime
import pytz
import logging
import time

LOCATION = "Toronto,CA"
OWM_API_KEY = os.environ['OWM_API_KEY']
SAMPLE_INTERVAL = 60 * 5 

owm = pyowm.OWM(OWM_API_KEY)
logger = logging.getLogger(__name__)

last_recorded_temp = None

def get_recent_temp():
    global last_recorded_temp
    if last_recorded_temp is None:
        sample_current_temp()
    return last_recorded_temp

def get_current_temp():
    logger.debug("Getting the current outside temp")
    try:
        return owm.weather_at_place(LOCATION).get_weather().get_temperature()['temp'] - 273.15
    except:
        logger.exception("Error getting the temperature, retrying")
        time.sleep(5)
        return get_current_temp()


def sample_current_temp():
    global last_recorded_temp
    last_recorded_temp = get_current_temp()

sampler = Sampler(SAMPLE_INTERVAL, sample_current_temp)


def start_recording():
    logger.info("Start sampling")
    sampler.start()
