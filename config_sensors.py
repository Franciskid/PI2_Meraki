# ================================= #
# Goal is to get automatically all  #
# sensors through the meraki api    #
# ================================= #

import requests
from config import base_url, meraki_api_key, network_id


types = {"MT10" : "temperature", "MT20" : "door"}

headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Cisco-Meraki-API-Key": meraki_api_key
    }

def get_sensors(metric):
    """
    Get all the sensors with the specified metric "temperature", "door", "humidity"
    """
    all_sensors = get_sensors_list()
    sensors = list()
    for sensor in all_sensors:
        if sensor['model'] in types:
            if types[sensor['model']] == metric:
                sensors.append({"serial" : sensor["serial"], "name" : sensor['name'], "type" : types[sensor['model']]})
    return sensors

def get_sensors_list():
    try:
        msg = requests.request('GET',
                               f"{base_url}/networks/{network_id}/devices",
                               headers=headers)
        if msg.ok:
            data = msg.json()
            return data
    except Exception as e:
        print("API Connection error: {}".format(e))
