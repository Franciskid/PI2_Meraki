# -*- coding: utf-8 -*-
"""
Created on Fri Jan 14 21:58:13 2022

@author: Francois
"""

import requests
from influxdb_client import Point, InfluxDBClient
from urllib3 import Retry

from config import base_url, meraki_api_key, network_id, influx_url, token, org, bucket, temperature_sensors, door_sensors, sensor_mapping
from influxdb_client.client.write_api import SYNCHRONOUS

import pandas as pd
import time


from datetime import datetime, timedelta
from meteostat import Point as meteoPoint, Hourly

# Influx DB Connector
retries = Retry(connect=10, read=5, redirect=10)
influx_client = InfluxDBClient(url=influx_url, token=token, org=org, retries=retries)
influx_db = influx_client.write_api(write_options=SYNCHRONOUS)


def get_historical_sensor_reading(sensor_serial, metric, timespan, resolution):
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
        "agg": "sds"
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

def get_name(serial):
    for x in sensor_mapping:
        if (x["serial"] == serial):
            return x["name"]
    return serial


def put_historical_data_into_influx_door(sensor_serial, timespan, resolution):
    """
    Insert historical data into InfluxDB - doors status
    """
    print(f"Saving {get_name(sensor_serial)} data into databse")
    try:
        doors_readings = get_historical_sensor_reading(sensor_serial, "door", timespan, resolution)
        
        print(doors_readings)
        df = pd.DataFrame(doors_readings[0]["data"])

        df = df.rename(columns={"ts": "ts", "value": "door"})
        df = df.set_index("ts")
        
        print (df)
        
        points = [Point(get_name(sensor_serial)).tag("location", "L404").field("door status", x.door).time(x.Index) for x in df.itertuples(index=True)]
        
        try:
            influx_db.write(
                bucket=bucket,
                org=org,
                record=points)
            print(f"{get_name(sensor_serial)} - Historical Temperature data successfully inserted.")
            
        except Exception as e:
                print(f"{get_name(sensor_serial)} - can't write to database: {e}")
        
    except Exception as e:
        print(f"{get_name(sensor_serial)} - can't insert into dataframe: {e}")
    
    
for s in door_sensors:
    put_historical_data_into_influx_door(s, 259200, 1)  # last 30 days, sensor reading every 2 min, average
    


    
    
    
    
    
    
    