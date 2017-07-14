
from collections import deque
from functools import reduce
from threading import Lock
import logging
from dht11 import dht11
from rpithermostat import sampler

logger = logging.getLogger(__name__)
temphumids = deque([], maxlen=30)
sensor = dht11.DHT11(26)
lock_temphumids = Lock()
measure_thread = None


def get_current_temphumid():
    with lock_temphumids:
        size = len(temphumids)
        avg_t = reduce(lambda tally, b: tally + b.temperature, temphumids, 0) / size
        avg_h = reduce(lambda tally, b: tally + b.humidity, temphumids, 0) / size
        retval = {'temperature':avg_t, 'humidity':avg_h}
        logging.debug("current temphumid %r" % retval)
        return retval

def record_temp():
    current = sensor.read()
    if current.is_valid():
        with lock_temphumids:
            temphumids.append(current)
    else:
        # retrying
        record_temp()


def start_recording():
    global measure_thread
    logging.info("Start recording")
    record_temp()
    measure_thread = sampler.Sampler(1, record_temp)
    measure_thread.start()
