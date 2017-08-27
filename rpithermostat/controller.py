
from RPi import GPIO
import logging

logger = logging.getLogger(__name__)

pin_heat = 16
pin_fan = 21
pin_cooling = 20

def heat(onoff):
    GPIO.output(pin_heat, onoff)
def fan(onoff):
    GPIO.output(pin_fan, onoff)
def cooling(onoff):
    GPIO.output(pin_cooling, onoff)

for pin in [pin_heat, pin_fan, pin_cooling]:
    GPIO.setup(pin, GPIO.OUT)
