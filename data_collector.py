"""
Copyright (c) 2021 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
               https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

import requests
from influxdb_client import Point, InfluxDBClient
from urllib3 import Retry

from config import base_url, meraki_api_key, network_id, influx_url, token, org, bucket
from config_sensors import get_sensors
from influxdb_client.client.write_api import SYNCHRONOUS

import pandas as pd
import numpy as np
import time


from datetime import datetime, timedelta
from meteostat import Point as meteoPoint, Hourly

# Influx DB Connector
retries = Retry(connect=10, read=5, redirect=10)
influx_client = InfluxDBClient(url=influx_url, token=token, org=org, retries=retries)
influx_db = influx_client.write_api(write_options=SYNCHRONOUS)


def find_network_sensors():
    '''Retreiving sensors in network'''
    print("Finding Sensors ...")
    global temperature_sensors
    global door_sensors
    temperature_sensors = get_sensors("temperature")
    door_sensors = get_sensors("door")
    temperature_sensors = sorted(temperature_sensors, key=lambda d: int(d['name']))
    door_sensors = sorted(door_sensors, key=lambda d: d['name'])
    print(f"{len(temperature_sensors) + len(door_sensors)} sensors found !\n")


def get_latest_sensor_reading(sensor, metric):
    """
    Get latest sensor reading from MT sensor
    metrics: 'temperature', 'humidity', 'water_detection' or 'door'
    """
    sensor_serial = sensor["serial"]

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Cisco-Meraki-API-Key": meraki_api_key
    }
    params = {
        "serials[]": sensor_serial,
        "metric": metric
    }
    try:
        msg = requests.request('GET',
                               f"{base_url}/networks/{network_id}/sensors/stats/latestBySensor",
                               headers=headers, params=params)
        if msg.ok:
            data = msg.json()
            return data
    except Exception as e:
        print("API Connection error: {}".format(e))

def get_latest_weather_reading():
    start = datetime.now() + timedelta(hours=-1)
    end = datetime.now()

    # Create Point for Courbevoie
    location = meteoPoint(48.896640253127785, 2.23684585029297, 53)

    lastHour = Hourly(location, start, end)
    lastHour = lastHour.fetch().iloc[0]
    lastHour.coco = float(0 if lastHour.name.hour < 8 or lastHour.name.hour > 20 or lastHour.coco >= 3 else 1)

    return lastHour


def get_historical_sensor_reading(sensor, metric, timespan, resolution):
    """
    Get historical sensor readings from MT sensor
    The valid resolutions are: 1, 120, 3600, 14400, 86400. The default is 120.
    """
    sensor_serial = sensor["serial"]

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

def get_historical_weather_reading():

    # Set time period
    start = datetime(2021, 12, 1)
    end = datetime.now()

    # Create Point for Courbevoie
    location = meteoPoint(48.896640253127785, 2.23684585029297, 53)

    # Get daily data for december till now
    data = Hourly(location, start, end)
    data = data.fetch()
    
    return data



def put_historical_data_into_influx_weather_temp_hum():
    try:
        data = get_historical_weather_reading()

        #To get the sunny moments, we need to filter out all the good weather points during night time
        #Better would be to find the exact time for each day when the sunrises and when the sunsets occur
        #Best would be to calculate precisely when the sun hits the windows, based on the orientation of the building
        data['time'] = pd.to_datetime(data.index)
        data['time'] = data['time'].apply(str)
        data['time'] = pd.to_datetime(data['time'], format='%Y-%m-%d %H:%M:%S')

        data.loc[data.time.dt.hour < 8, 'coco'] = 0
        data.loc[data.time.dt.hour > 20, 'coco'] = 0
        data.loc[data.coco >= 3, 'coco'] = 0

        data.loc[(data.coco == 1) | (data.coco == 2), 'coco'] = 1

        points = [Point("Weather").
                  tag("location", "Pôle LdV").
                  field("temperature", x.temp).
                  field("humidity", x.rhum).
                  field("sunny", x.coco).
                  time(x.Index) for x in data.itertuples(index=True)]

        try:
            influx_db.write(
                bucket=bucket,
                org=org,
                record=points)
            print("Weather data - Historical Temperatures/Humidity data successfully inserted.")
        except Exception as e:
            print(f"Weather data - can't write to database: {e}")

    except Exception as e:
        print(f"Weather data - can't add date to dataframe: {e}")

def put_historical_data_into_influx_door(sensor, timespan, resolution):
    """
    Insert historical data into InfluxDB - doors status
    """
    print(f"Saving '{sensor['name']}' sensor data into database")
    try:
        doors_readings = get_historical_sensor_reading(sensor, "door", timespan, resolution)
        df = pd.DataFrame(doors_readings[0]["data"])

        df = df.rename(columns={"ts": "ts", "value": "door"})
        df = df.set_index("ts")
        
        print (df)
        
        points = [Point(sensor['name']).
                  tag("location", "L404").
                  field("door status", x.door).
                  time(x.Index) for x in df.itertuples(index=True)]
        
        try:
            influx_db.write(
                bucket=bucket,
                org=org,
                record=points)
            print(f"'{sensor['name']}' sensor -  Historical Temperature data successfully inserted.\n")
            
        except Exception as e:
                print(f"'{sensor['name']}' sensor - can't write to database: {e}")
        
    except Exception as e:
        print(f"'{sensor['name']}' sensor - can't insert into dataframe: {e}")

def put_historical_data_into_influx_temp_hum(sensor, timespan, resolution):
    """
    Insert historical data into InfluxDB - temperature + humidity only
    """
    print(f"Saving '{sensor['name']}' sensor data into database")
    try:
        temperature_readings = get_historical_sensor_reading(sensor, "temperature", timespan, resolution)
        df = pd.DataFrame(temperature_readings[0]["data"])

        df = df.rename(columns={"ts": "ts", "value": "temperature"})
        df = df.set_index("ts")

        humidity_readings = get_historical_sensor_reading(sensor, "humidity", timespan, resolution)
        df_hum = pd.DataFrame(humidity_readings[0]["data"])
        df_hum = df_hum.rename(columns={"ts": "ts", "value": "humidity"})
        df_hum = df_hum.set_index("ts")

        df = pd.concat([df, df_hum], axis=1, join="inner")

        points = [Point(sensor['name']).
                      tag("location", "L404").
                      field("temperature", x.temperature).
                      field("humidity",x.humidity).
                      time(x.Index) for x in df.itertuples(index=True)]


    except Exception as e:
        print(f"'{sensor['name']}' sensor -  can't insert into dataframe: {e}")

    try:
        influx_db.write(
            bucket=bucket,
            org=org,
            record=points)
        print(f"'{sensor['name']}' sensor - Historical Temperature/Humidity data successfully inserted.\n")
    except Exception as e:
        print(f"'{sensor['name']}' sensor - can't write to database: {e}")



def main():
    find_network_sensors()


    print("\n***** HISTORICAL DATA COLLECTION ****** \n\n")

    print("** Weather DATA *** \n")
    put_historical_data_into_influx_weather_temp_hum() # from dec to now, weather data every hour

    print("\n\n** TEMP/HUMID DATA *** \n")
    for s in temperature_sensors:
        put_historical_data_into_influx_temp_hum(s, 2592000, 3600)  # last 30 days, sensor reading every 60 min, average

    print("\n\n** DOORS DATA *** \n") #Problem with the API "/sensors/stats/historicalBySensor" metric="door", returns nothing
    for s in door_sensors:
        put_historical_data_into_influx_door(s, 2592000, 120)  # last 30 days, sensor reading every min, average

    print("\n--------------------------------------- \n")


    print("\n******* DATA UPDATE EVERY HOUR ******** \n\n")
    while True:

        try:
            #Weather
            lastHour = get_latest_weather_reading()
            
            influx_db.write(
                    bucket=bucket,
                    org=org,
                    record=Point("Weather")
                        .tag("location", "Pôle LdV")
                        .field("temperature", lastHour.temp)
                        .field("humidity", lastHour.rhum)
                        .field("sunny", lastHour.coco)
                        .time(lastHour.name))
            
            print("last weather data added to db**\n")

            #Temperatures
            for temp in temperature_sensors:
                r = get_latest_sensor_reading(temp, "temperature")[0]
                r_hum = get_latest_sensor_reading(temp, "humidity")[0]
                
                influx_db.write(
                    bucket=bucket,
                    org=org,
                    record=Point(temp["name"])
                        .field("temperature", r["value"])
                        .field("humidity", r_hum["value"])
                        .time(r["ts"]).tag('location', "L404"))
                print(f"{temp['name']} last data added to db**")

           #Humidity
            for door in door_sensors:
                opened = get_latest_sensor_reading(door, "door")[0]
                
                influx_db.write(
                    bucket=bucket,
                    org=org,
                    record=Point(door["name"])
                        .field("door status", opened["value"])
                        .time(opened["ts"]).tag('location', "L404"))
                print(f"{door['name']} last data added to db**")
                    
            
        except Exception as e:
             print("Can't write to database: {}".format(e))
             
        print("\n***time for sleep***\n")
        time.sleep(30)


main()


