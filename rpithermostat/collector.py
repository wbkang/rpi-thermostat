
import csv
from rpithermostat import temphumids
from rpithermostat import outside_weather
from datetime import datetime
from tzlocal import get_localzone

out_file = "/home/pi/temp_collection.csv"



def record_reaction(reaction):
    """ reaction is -1 for cold , 0 for ok, 1 for hot """
    ts = datetime.now().isoformat()
    th = temphumids.get_current_temphumid()
    ot = outside_weather.get_recent_temp()
    with open(out_file, 'a') as f:
        w = csv.writer(f)
        w.writerow([ts, th['temperature'], th['humidity'], ot, reaction])
    
