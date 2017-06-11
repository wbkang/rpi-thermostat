from threading import Lock
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, asc, desc, Boolean, and_, not_
from sqlalchemy.sql import select, delete
from sqlalchemy.schema import Index
from sqlalchemy.types import TIMESTAMP, Float
from rpiweather import config
import logging
import pytz
import datetime
import pandas as pd

logger = logging.getLogger(__name__)
metadata = MetaData()

meteo_table = Table('meteo', metadata,
                          Column('time', TIMESTAMP(timezone=True)),
                          Column('type', String),
                          Column('value', Float),
                          Column('preaggregated', Boolean)) # not True means not aggregated

Index("meteo_time", meteo_table.c.time)

data_lock = Lock()

db_path = config.data['conn_string']
engine = create_engine(db_path, echo=False)
metadata.create_all(engine)

def insert_data(dt, type_, value):
    with data_lock:
        with engine.connect() as conn:
            logger.debug("Inserting data (%s, %s, %s)" % (dt, type_, value))
            ins = meteo_table.insert().values(time=dt, type=type_, value=value, preaggregated=False)
            conn.execute(ins)



def get_recent_datapoints(lookbehind):
    from_time = datetime.datetime.now(pytz.utc).\
            replace(hour=0, minute=0, second=0, microsecond=0) - datetime.timedelta(hours=lookbehind)
    with data_lock:
        with engine.connect() as conn:
            sel = select([meteo_table.c.time, meteo_table.c.type, meteo_table.c.value]).\
                    where(meteo_table.c.time > from_time).\
                    order_by(asc("time"))
            return list(conn.execute(sel))

def prune_old_data():
    yesterday = datetime.datetime.now(pytz.utc).\
            replace(hour=0, minute=0, second=0, microsecond=0) - datetime.timedelta(days=1)
    with data_lock:
        with engine.connect() as conn:
            sel = select([meteo_table.c.time, meteo_table.c.type, meteo_table.c.value]).\
                    where(and_(
                        meteo_table.c.time < yesterday,
                        not_(meteo_table.c.preaggregated.is_(True)))).\
                    order_by(asc('time'))
            old_dp = list(conn.execute(sel))
            print("Fetched %d old datapoints" % len(old_dp))
            d = meteo_table.delete().\
                    where(meteo_table.c.time < yesterday)
            conn.execute(d)

            df = pd.DataFrame(old_dp, columns=['time', 'type', 'value'])
            df['time'] = pd.to_datetime(df['time'])
            df = df.set_index('time')
            pivot_df = df.pivot(columns='type', values='value').resample("15T").mean()
            count = 0
            for col in 'temperature', 'outside_temperature', 'pressure', 'humidity', 'dust':
                agg_df = pivot_df[col]
                for dt, val in zip(agg_df.index, agg_df):
                     ins = meteo_table.insert().values(time=dt, type=col, value=val, preaggregated=True)
                     conn.execute(ins)
                     count += 1
            print("Inserted %d aggregated rows" % count)
