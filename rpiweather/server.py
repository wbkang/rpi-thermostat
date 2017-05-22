#!/usr/bin/env python3

import rpiweather.mpl115a2
import RPi.GPIO as GPIO
import time
import threading
import logging
import pandas as pd
import numpy as np



logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(message)s')
GPIO.setmode(GPIO.BCM)

logger = logging.getLogger(__name__)


from rpiweather import temphumid
from rpiweather import temppressure 

temppressure.start_recording()
temphumid.start_recording()

def make_agg_df(rec):
    df = pd.DataFrame.from_records(rec, index="time")
    df.index = pd.to_datetime(df.index, unit="s")
    return df.resample("T").mean()

def magic():
    df_tp = make_agg_df(temppressure.get_records())
    df_th = make_agg_df(temphumid.get_records())
    df_th = df_th.rename(columns={'temp':'bad_temp'})
    total_view = pd.concat([df_tp, df_th], axis=1)
    return total_view

import IPython
IPython.embed()

