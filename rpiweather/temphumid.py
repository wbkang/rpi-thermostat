from dht11 import dht11
import logging
import threading
from rpiweather.sampler import Sampler
from collections import deque
import time

PIN_DHT = 4
SAMPLE_INTERVAL = 1

logger = logging.getLogger(__name__)

temp_sensor = dht11.DHT11(pin=PIN_DHT)
data = deque(maxlen=24 * 60 * 60)
data_lock = threading.Lock()


def get_records():
    with data_lock:
        return list(data)


def measure():
    return temp_sensor.read()


def accept_record(record):
    with data_lock:
        if record.is_valid():
            logger.debug("Record: temp_avg:%r hum_avg:%r" %
                         (record.temperature, record.humidity))
            data.append({'time': time.time(), 'temp': record.temperature,
                         'humidity': record.humidity})


sampler = Sampler(SAMPLE_INTERVAL, measure, accept_record)


def start_recording():
    logger.info("Start sampling")
    sampler.start()
