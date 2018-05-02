
from rpithermostat import temphumids
import datetime
import logging
from rpithermostat import pconfig
from rpithermostat import sampler
from rpithermostat.controller import fan, heatpump, heat
from rpithermostat import display

logger = logging.getLogger(__name__)

def off_governor():
    target_temp = get_target_temperature()
    current = temphumids.get_current_temphumid()
    current_temp = current['temperature']
    current_humidity = current['humidity']
    target_humidity = get_target_humidity() 
    heat(False)
    fan(False)
    heatpump(False)
    display.set_status2("Off")
off_governor.hb_num = 0

def should_circulate_air():
    dt = datetime.datetime.now()
    force_fan_on = dt.minute % 10 <= 2

def cool_governor():
    target_temp = get_target_temperature()
    current = temphumids.get_current_temphumid()
    current_temp = current['temperature']
    current_humidity = current['humidity']
    target_humidity = get_target_humidity() 
    
    if current_temp >= target_temp:
        heat(False)
        fan(True)
        heatpump(True)
        display.set_status2("Cooling")
    # elif current_humidity >= target_humidity:
    #     heat(False)
    #     fan(False)
    #     heatpump(True)
    #     display.set_status2("Dehumidifying")
    else:
        heat(False)
        fan(should_circulate_air())
        heatpump(False)
        display.set_status2("Idle")
cool_governor.hb_num = 2 

def heat_governor():
    target_temp = get_target_temperature()
    current = temphumids.get_current_temphumid()
    current_temp = current['temperature']
    current_humidity = current['humidity']
    target_humidity = get_target_humidity() 
    force_fan_on = should_circulate_air()
    
    if current_temp >= target_temp:
        heat(False)
        fan(False or force_fan_on)
        heatpump(False)
        display.set_status2("Idle")
    else:
        heat(True)
        fan(True or force_fan_on)
        heatpump(True)
        display.set_status2("Heating")
heat_governor.hb_num = 1 

def is_night():
    return False # disable for now
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

governor_map = {"cool": cool_governor,
                "heat": heat_governor,
                "off": off_governor}

def get_governor():
    return governor_map[pconfig.read_config_value(pconfig.KEY_GOVERNOR) or "off"]

def set_governor(g):
    gov = governor_map.get(g, None)
    if gov is not None:
        pconfig.write_config_value(pconfig.KEY_GOVERNOR, g)
        return
    raise Exception("Unknown governor %s" % g)

def temp_manager():
    current = temphumids.get_current_temphumid()
    display.set_status1("%.0fC%.0f%%->%dC%.0f%%" % (current['temperature'],
                                                    current['humidity'],
                                                    get_target_temperature(),
                                                    get_target_humidity()))
    get_governor()()

manager_thread = None

def start():
    global manager_thread
    manager_thread = sampler.Sampler(30, temp_manager)
    manager_thread .start()
