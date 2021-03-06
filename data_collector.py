import requests
from influxdb_client import Point, InfluxDBClient
from urllib3 import Retry

from config import *
from config_sensors import get_sensors
from influxdb_client.client.write_api import SYNCHRONOUS

import pandas as pd
import numpy as np
import time
import pytz


from datetime import datetime, timedelta, tzinfo
from meteostat import Point as meteoPoint, Hourly
from suntime import Sun, SunTimeException

# Influx DB Connector
retries = Retry(connect=10, read=5, redirect=10)
influx_client = InfluxDBClient(url=influx_url, token=token, org=org, retries=retries)
influx_db = influx_client.write_api(write_options=SYNCHRONOUS)


#Sunset and sunrise
sun = Sun(weather_location["lat"], weather_location["lon"])


def find_network_sensors():
    """
    Retreiving sensors in network
    """
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

    #sunrise now
    today_sr = sun.get_sunrise_time()
    today_ss = sun.get_sunset_time()

    # Create Point for Courbevoie
    location = meteoPoint(weather_location["lat"], weather_location["lon"], weather_location["alt"])

    lastHour = Hourly(location, start, end)
    lastHour = lastHour.fetch().iloc[0]
    lastHour.coco = float(0 if (lastHour.name.replace(tzinfo=pytz.timezone("Europe/Paris")) + timedelta(hours=-2)) < today_sr or (lastHour.name.replace(tzinfo=pytz.timezone("Europe/Paris")) + timedelta(hours=2)) > today_ss or lastHour.coco >= 3 else 1 if lastHour.coco <= 2 else 0)
    

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
    location = meteoPoint(weather_location["lat"], weather_location["lon"], weather_location["alt"])

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


        for index, row in data.iterrows():
            #sunrise and sunset
            sunrise = sun.get_local_sunrise_time(index)
            sunset = sun.get_local_sunset_time(index)

            row.coco = 0 if (row.time.replace(tzinfo=pytz.timezone("Europe/Paris")) + timedelta(hours=-2)) < sunrise or (row.time.replace(tzinfo=pytz.timezone("Europe/Paris")) + timedelta(hours=2)) > sunset or row.coco > 2 else 1 if row.coco <= 2 else 0
            data.loc[index] = row

        points = [Point("Weather").
                  tag("location", "P??le LdV").
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
        print(f"Weather data - can't add data to dataframe: {e}")

def put_historical_data_into_influx_door(sensor, timespan, resolution):
    """
    Insert historical data into InfluxDB - doors status
    """
    print(f"Saving '{sensor['name']}' sensor data into database")
    try:
        doors_readings = get_historical_sensor_reading(sensor, "door", timespan, resolution)
        df = pd.DataFrame(doors_readings[0]["data"])
        df = df.set_index("ts")

        points = [Point(sensor['name']).
                  tag("location", "L404").
                  field("door_status", x.value).
                  time(x.Index) for x in df.itertuples(index=True)]

        try:
            influx_db.write(
                bucket=bucket,
                org=org,
                record=points)
            print(f"'{sensor['name']}' sensor -  Historical Door data successfully inserted.\n")
            
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


    print("***** HISTORICAL DATA COLLECTION ****** \n")

    print("** Weather DATA *** \n")
    put_historical_data_into_influx_weather_temp_hum() # from dec to now, weather data every hour

    print("\n\n** TEMP/HUMID DATA *** \n")
    for s in temperature_sensors:
        put_historical_data_into_influx_temp_hum(s, 2592000, 3600)  # last 30 days, sensor reading every 60 min, average

    print("\n\n** DOORS DATA *** \n") #Problem with the API for boolean type sensors
    for s in door_sensors:
        put_historical_data_into_influx_door(s, 2592000, 3600)

    # for s in door_sensors:
    #     for day in range(0, 30):
    #         t1 = (datetime.now() + timedelta(days=-day)).isoformat("T") + "Z"
    #         t0 = (datetime.now() + timedelta(days=-day - 1)).isoformat("T") + "Z"
    #         print("t0: ", t0, "   t1: ", t1)
    #         put_historical_data_into_influx_door(s, t1, t0, 120)  # last 30 days, sensor reading every hour, average. Every 2 min fails

    print("\n------------------------------------------------------------------------- \n")


    print("\n******* DATA UPDATE EVERY HOUR ******** \n\n")
    while True:

        try:
            #Weather
            lastHour = get_latest_weather_reading()
            
            influx_db.write(
                    bucket=bucket,
                    org=org,
                    record=Point("Weather")
                        .tag("location", "P??le LdV")
                        .field("temperature", lastHour.temp)
                        .field("humidity", lastHour.rhum)
                        .field("sunny", lastHour.coco)
                        .time(lastHour.name))
            
            print("**last weather data added to db\n")

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
                print(f"**'{temp['name']}' sensor last data added to db")

           #Doors
            for door in door_sensors:
                opened = get_latest_sensor_reading(door, "door")[0]
                
                influx_db.write(
                    bucket=bucket,
                    org=org,
                    record=Point(door["name"])
                        .field("door_status", opened["value"])
                        .time(opened["ts"]).tag('location', "L404"))
                print(f"**'{door['name']}' sensor last data added to db")
                    
            
        except Exception as e:
             print("Can't write to database: {}".format(e))
             
        print("\n***time for sleep***\n")
        time.sleep(30)

if __name__ == "__main__":
    main()


