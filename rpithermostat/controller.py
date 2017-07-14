
from RPi import GPIO
from rpithermostat import sampler
from rpithermostat import oracle
from rpithermostat import display 
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


def temp_manager():
    if oracle.should_cool():
        logger.info("Too hot! Start cooling")
        fan(True)
        heat(False)
        cooling(True)
        display.set_status("Cooling")
    else:
        logger.info("Too cold! Idling")
        fan(True)
        heat(False)
        cooling(False)
        display.set_status("Idle")

manager_thread = None

def start():
    global manager_thread
    for pin in [pin_heat, pin_fan, pin_cooling]:
        GPIO.setup(pin, GPIO.OUT)
    manager_thread = sampler.Sampler(30, temp_manager)
    manager_thread .start()
