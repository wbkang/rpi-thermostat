
from rpithermostat import temphumids
import datetime
import logging
from rpithermostat import pconfig

logger = logging.getLogger(__name__)

def is_night():
    dt = datetime.datetime.now()
    return not (dt.hour >= 8 and dt.hour < 22)

def get_target_temperature():
    return pconfig.read_config_value(pconfig.KEY_TEMP_NIGHT if is_night() else pconfig.KEY_TEMP_DAY) or 25

def set_target_temperature(temp):
    return pconfig.write_config_value(pconfig.KEY_TEMP_NIGHT if is_night() else pconfig.KEY_TEMP_DAY, temp)

def should_cool():
    target_temp = get_target_temperature()
    current = temphumids.get_current_temphumid()
    current_temp = current['temperature']
    current_humidity = current['humidity']
    target_humidity = 40
    logger.info("Current temperature: %d, Target: %d" % (current_temp, target_temp))
    return current_temp >= target_temp# or (not is_night() and current_humidity >= target_humidity )
