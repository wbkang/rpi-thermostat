import logging
from rpiweather.sampler import Sampler
from rpiweather.data import insert_data
from rpiweather import config
from rpiweather import cdust
import datetime
import pytz
import time

mcp3008_config = config.dust['mcp3008']
CLK = mcp3008_config['clk']
MISO = mcp3008_config['miso']
MOSI = mcp3008_config['mosi']
CS = mcp3008_config['cs']

LED = mcp3008_config['led']

SAMPLE_INTERVAL = config.dust['sample_interval']

logger = logging.getLogger(__name__)

cdust.setup(clk=CLK, din=MISO, dout=MOSI, cs=CS, led=LED)

def measure():
    "Return the dust value, out of 100"
    val = cdust.read(1)
    retval = 100 * val / 1024
    logging.debug("Raw value %d" % val)
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
