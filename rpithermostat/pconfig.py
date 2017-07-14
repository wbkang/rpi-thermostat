import json
import os.path

config_file = "/home/pi/.thermostat.json"

KEY_TEMP_DAY = "temp.day"
KEY_TEMP_NIGHT = "temp.night"

def read_config():
    if os.path.isfile(config_file):
        with open(config_file, 'rb') as f:
            return json.loads(f.read().decode("utf8"))
    else:
        return dict()

def write_config(d):
    with open(config_file, 'wb') as f:
        f.write(json.dumps(d).encode("utf8"))

def read_config_value(key):
    return read_config().get(key, None)

def write_config_value(key, value):
    c = read_config()
    c[key] = value
    write_config(c)
