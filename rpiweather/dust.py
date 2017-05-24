import logging
from rpiweather.sampler import Sampler
from rpiweather.data import insert_data
import datetime
import pytz
import Adafruit_MCP3008
from RPi import GPIO
import time

CLK = 18
MISO = 23
MOSI = 24
CS = 25

LED = 17

SAMPLE_INTERVAL = 30 

GPIO.setup(LED, GPIO.OUT)
logger = logging.getLogger(__name__)

# bit-bang SPI interface
mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)

def measure():
    "Return the dust value, out of 100"
    maxval = 0
    for x in range(0, 20):
        GPIO.output(LED, GPIO.LOW)
        time.sleep(0.2) # capacitor charging
        GPIO.output(LED, GPIO.HIGH)
        
        # I am supposed to measure the peak after 0.28ms
        # but RPi can't do that. So I start reading right away
        # Sample the highest value.
        now = time.monotonic()
        for x in range(10):
            maxval = max(mcp.read_adc(1), maxval)
    GPIO.output(LED, GPIO.LOW)
    retval = 100 * maxval / 1024
    logging.debug("Raw value %d" % maxval)
    logging.debug("Dust value measured: %d%%" % retval)
    return retval

def sample():
    val = measure()
    now = datetime.datetime.now(pytz.utc)
    insert_data(now, "dust", val)

sampler = Sampler(SAMPLE_INTERVAL, sample)

def start_recording():
    logger.info("Start sampling")
    sampler.start()
