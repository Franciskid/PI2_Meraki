
import requests

from config import base_url, meraki_api_key, network_id, influx_url, token, org, bucket
from config_sensors import get_sensors

import pandas as pd
import numpy as np
import time


from datetime import datetime, timedelta
from meteostat import Point as meteoPoint, Hourly


def get_historical_sensor_reading(sensor_serial, metric, t0, t1, resolution):
    """
    Get historical sensor readings from MT sensor
    The valid resolutions are: 1, 120, 3600, 14400, 86400. The default is 120.
    """
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Cisco-Meraki-API-Key": meraki_api_key
    }

    params = {
        "serials[]": sensor_serial,
        "metric": metric,
        "t0": t0,
        "t1": t1,
        "resolution": resolution,
        "agg": "max"
    }
    try:
        msg = requests.request('GET',
                               f"{base_url}/networks/{network_id}/sensors/stats/historicalBySensor",
                               headers=headers, params=params)
        if msg.ok:
            data = msg.json()
            return data
    except Exception as e:
        print("API Connection error: {}".format(e))

def get_historical_sensor_reading_(sensor_serial, metric, timespan, resolution):
    """
    Get historical sensor readings from MT sensor
    The valid resolutions are: 1, 120, 3600, 14400, 86400. The default is 120.
    """
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Cisco-Meraki-API-Key": meraki_api_key
    }

    params = {
        "serials[]": sensor_serial,
        "metric": metric,
        "timespan": timespan,
        "resolution": resolution,
        "agg": "max"
    }
    try:
        msg = requests.request('GET',
                               f"{base_url}/networks/{network_id}/sensors/stats/historicalBySensor",
                               headers=headers, params=params)
        if msg.ok:
            data = msg.json()
            return data
    except Exception as e:
        print("API Connection error: {}".format(e))


door_data = get_historical_sensor_reading("Q3CC-CHNP-XUTA", "door", "2022-01-17T08:40:00.000000Z", "2022-01-17T09:00:00.000000Z", 120)
#door_data = get_historical_sensor_reading_("Q3CC-CHNP-XUTA", "door", "25920", 120)
#temp_data = get_historical_sensor_reading("Q3CA-3Y93-LACF", "temperature", 2592000, 3600)

print(door_data)
#print(temp_data)

df = pd.DataFrame(door_data[0]["data"])
df = df.rename(columns={"ts": "ts", "value": "door"})
df = df.set_index("ts")

print(df)#[df["door"]<=1.0])