
from rpithermostat import temphumids
import datetime
import logging
from rpithermostat import pconfig
from rpithermostat import sampler
from rpithermostat.controller import fan, cooling, heat
from rpithermostat import display

logger = logging.getLogger(__name__)

def cool_governor():
    target_temp = get_target_temperature()
    current = temphumids.get_current_temphumid()
    current_temp = current['temperature']
    current_humidity = current['humidity']
    target_humidity = get_target_humidity() 
    
    if current_temp >= target_temp:
        heat(False)
        fan(True)
        cooling(True)
        display.set_status2("Cooling")
    elif current_humidity >= target_humidity:
        heat(False)
        fan(False)
        cooling(True)
        display.set_status2("Dehumidifying")
    else:
        heat(False)
        fan(False)
        cooling(False)
        display.set_status2("Idle")

def is_night():
    dt = datetime.datetime.now()
    return not (dt.hour >= 8 and dt.hour < 22)

def get_target_temperature():
    return pconfig.read_config_value(pconfig.KEY_TEMP_NIGHT if is_night() else pconfig.KEY_TEMP_DAY) or 25

def set_target_temperature(temp):
    return pconfig.write_config_value(pconfig.KEY_TEMP_NIGHT if is_night() else pconfig.KEY_TEMP_DAY, temp)

def get_target_humidity():
    return pconfig.read_config_value(pconfig.KEY_HUMIDITY) or 25

def set_target_humidity(h):
    return pconfig.write_config_value(pconfig.KEY_HUMIDITY, h)

def temp_manager():
    current = temphumids.get_current_temphumid()
    display.set_status1("%.0fC%.0f%%->%dC%.0f%%" % (current['temperature'],
                                                    current['humidity'],
                                                    get_target_temperature(),
                                                    get_target_humidity()))
    current_governor()

manager_thread = None
current_governor = cool_governor

def start():
    global manager_thread
    manager_thread = sampler.Sampler(30, temp_manager)
    manager_thread .start()
