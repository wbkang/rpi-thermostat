from dht11 import dht11
import logging
import threading
from rpiweather.sampler import Sampler
from rpiweather.data import insert_data
from collections import deque
import time
import datetime
import pytz

PIN_DHT = 4
SAMPLE_INTERVAL = 30

logger = logging.getLogger(__name__)

temp_sensor = dht11.DHT11(pin=PIN_DHT)


def measure():
    return temp_sensor.read()


def accept_record(record):
    if record.is_valid():
        logger.debug("Record: temp_avg:%r hum_avg:%r" %
                     (record.temperature, record.humidity))
        now = datetime.datetime.now(pytz.utc)
        insert_data(now, "temperature", record.temperature)
        insert_data(now, "humidity", record.humidity)


sampler = Sampler(SAMPLE_INTERVAL, measure, accept_record)


def start_recording():
    logger.info("Start sampling")
    sampler.start()
