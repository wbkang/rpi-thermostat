import pyowm
import os

LOCATION = "Toronto,CA"
OWM_API_KEY = os.environ['OWM_API_KEY']

owm = pyowm.OWM(OWM_API_KEY)

def will_rain_today(self):
    return self.owm.daily_forecast(self.location, limit=1).will_have_rain()
    
def current_temp(self):
    owm.weather_at_place(self.location).get_weather().get_temperature()['temp'] - 273.15

