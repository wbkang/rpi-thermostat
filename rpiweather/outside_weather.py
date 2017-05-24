import pyowm
import os
from rpiweather.sampler import Sampler
from rpiweather.data import insert_data
import datetime
import pytz
import logging

LOCATION = "Toronto,CA"
OWM_API_KEY = os.environ['OWM_API_KEY']
SAMPLE_INTERVAL = 60 * 5 

owm = pyowm.OWM(OWM_API_KEY)
logger = logging.getLogger(__name__)


def will_rain_today():
    return owm.daily_forecast(LOCATION, limit=1).will_have_rain()


def get_current_temp():
    logger.debug("Getting the current outside temp")
    return owm.weather_at_place(LOCATION).get_weather().get_temperature()['temp'] - 273.15


def sample_current_temp():
    t = get_current_temp()
    now = datetime.datetime.now(pytz.utc)
    insert_data(now, "outside_temperature", t)

sampler = Sampler(SAMPLE_INTERVAL, sample_current_temp)


def start_recording():
    logger.info("Start sampling")
    sampler.start()
