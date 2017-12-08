
from RPi import GPIO
import logging

logger = logging.getLogger(__name__)

pin_heat = 16
pin_fan = 21
pin_heatpump = 20

def heat(onoff):
    GPIO.output(pin_heat, onoff)
def fan(onoff):
    GPIO.output(pin_fan, onoff)
def heatpump(onoff):
    GPIO.output(pin_heatpump, onoff)

for pin in [pin_heat, pin_fan, pin_heatpump]:
    GPIO.setup(pin, GPIO.OUT)
