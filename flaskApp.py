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

import threading
import time
from datetime import datetime, timedelta

import jmespath
import pytz
import requests
from flask import (Flask, json, flash, redirect, render_template, request, send_file,
                   url_for)

from config import (ASHRAE_high, ASHRAE_low, meraki_api_key, network_id,
                    sensor_mapping)
from config_sensors import get_sensors
from alert_profiles import alerts
from data_collector import get_latest_sensor_reading
from heatmap_creation import get_heatmap
from energy_savings import get_energy_infos, optimum_temp


app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
alertprofiles_to_snooze = []


@app.route('/', methods=['GET'])
def index():
    flash(alerts())
    return render_template("start_page.html")


@app.route('/heatmap', methods=['GET', 'POST'])
def heatmap():
    t_min,t_max,gap = get_heatmap()

    return render_template("heatmap.html",
                           t_min=t_min,
                           t_max=t_max,
                           gap=gap)

@app.route('/energy_management', methods=["GET","POST"])
def energy_management():
    optimum_reduction, weekly_energy_expenses,monthly_energy_saved=get_energy_infos()
    energy_expenses_sentence1 ="We estimate in the last 7 days that you spent "
    energy_expenses_sentence2=str(weekly_energy_expenses)+"€"
    energy_expenses_sentence3=" for the temperature regulation in your room."
    optimum_reduction_sentence1 =str("The optimum temperature in an office is "+str(optimum_temp)+"°C so we advice you to change the temperature by ")
    optimum_reduction_sentence2 =str(optimum_reduction)+"°C"

    return render_template("energy_management.html", weekly_energy_expenses1=energy_expenses_sentence1,
                                                     weekly_energy_expenses2=energy_expenses_sentence2,
                                                     weekly_energy_expenses3=energy_expenses_sentence3,
                                                     optimum_reduction1=optimum_reduction_sentence1,
                                                     optimum_reduction2=optimum_reduction_sentence2,
                                                     monthly_energy_saved=str(monthly_energy_saved)+"€")

@app.route('/snooze_sensors', methods=['GET', 'POST'])
def snooze_sensors():
    global alertprofiles_to_snooze

    req = request.form
    sensor_name = request.args.get('sensor')
    for sen in sensor_mapping:
        if sen['name'] == sensor_name:
            sensor_serial = sen['serial']

    prefix_alertprofiles = "checkbox-"
    alertprofiles_dict = {key: val for key, val in req.items() if key.startswith(prefix_alertprofiles)}
    alertprofiles_to_snooze = []
    for key in alertprofiles_dict.keys():
        short_key = key.replace("checkbox-", "")
        short_key_dict = {
            'name': short_key,
            'snoozed_sensors': []
        }
        alertprofiles_to_snooze.append(short_key_dict)

    global alert_profiles
    global alert_profiles_overview

    # put requests to take sensors off alert profiles
    if sensor_name != None:  # for a single sensor
        for ap in alert_profiles:
            for ap_to_snooze in alertprofiles_to_snooze:
                sensorlist_putrequest = ap['applied_sensors']
                if ap['name'] == ap_to_snooze['name']:
                    sensorlist_putrequest.remove(sensor_serial)
                    sensorlist_putrequest = list(dict.fromkeys(sensorlist_putrequest))
                    ap_to_snooze['id'] = ap['id']
                    ap_to_snooze['snoozed_sensors'].append(sensor_serial)

                    url = 'https://api.meraki.com/api/v1/networks/' + network_id + '/sensors/alerts/profiles/' + \
                          ap_to_snooze['id']
                    headers = {
                        'X-Cisco-Meraki-API-Key': meraki_api_key,
                        'Accept': 'application/json',
                        'Content-Type': 'application/json'
                    }
                    get_alert_profile = requests.get(url, headers=headers, verify=False)
                    response = get_alert_profile.json()
                    data = {
                        'name': response['name'],
                        'scheduleId': response['scheduleId'],
                        'conditions': response['conditions'],
                        'recipients': response['recipients'],
                        'serials': sensorlist_putrequest
                    }
                    put_alert_profile = requests.put(url, headers=headers, data=json.dumps(data), verify=False)
                    print(put_alert_profile)

                    snooze_minutes = (int(req['snooze_minutes']) * 60) + 13
                    tz_London = pytz.timezone('Europe/London')
                    timedelta_snooze = (datetime.now(tz_London) + timedelta(seconds=snooze_minutes)).strftime(
                        "%H:%M:%S")
                    snooze_until = str(timedelta_snooze)
                    ap_to_snooze['snooze_until'] = snooze_until

    else:  # for all sensors
        for ap in alert_profiles_overview:
            for ap_to_snooze in alertprofiles_to_snooze:
                if ap['name'] == ap_to_snooze['name']:
                    ap_to_snooze['id'] = ap['id']
                    for sen in sensor_mapping:
                        sensorlist_putrequest = ap['applied_sensors']
                        if sen['serial'] in sensorlist_putrequest:
                            sensorlist_putrequest.remove(sen['serial'])
                            ap_to_snooze['snoozed_sensors'].append(sen['serial'])
                    sensorlist_putrequest = list(dict.fromkeys(sensorlist_putrequest))
                    url = 'https://api.meraki.com/api/v1/networks/' + network_id + '/sensors/alerts/profiles/' + \
                          ap_to_snooze['id']
                    headers = {
                        'X-Cisco-Meraki-API-Key': meraki_api_key,
                        'Accept': 'application/json',
                        'Content-Type': 'application/json'
                    }
                    get_alert_profile = requests.get(url, headers=headers, verify=False)
                    response = get_alert_profile.json()
                    data = {
                        'name': response['name'],
                        'scheduleId': response['scheduleId'],
                        'conditions': response['conditions'],
                        'recipients': response['recipients'],
                        'serials': sensorlist_putrequest
                    }
                    put_alert_profile = requests.put(url, headers=headers, data=json.dumps(data), verify=False)
                    print(put_alert_profile)

                    snooze_minutes = (int(req['snooze_minutes']) * 60) + 10
                    tz_London = pytz.timezone('Europe/London')
                    timedelta_snooze = (datetime.now(tz_London) + timedelta(seconds=snooze_minutes)).strftime(
                        "%H:%M:%S")
                    snooze_until = str(timedelta_snooze)
                    ap_to_snooze['snooze_until'] = snooze_until

    # countdown to put them back on alert profile after x minutes
    th = threading.Thread(target=snoozing, args=[alertprofiles_to_snooze, snooze_minutes])
    th.start()

    if sensor_name == None:
        sensor_name = 'all'

    return redirect(url_for('.heatmap', sensor=sensor_name))


def snoozing(alertprofiles_to_snooze, snooze_minutes):
    time.sleep(snooze_minutes)

    for ap_to_snooze in alertprofiles_to_snooze:
        url = 'https://api.meraki.com/api/v1/networks/' + network_id + '/sensors/alerts/profiles/' + ap_to_snooze['id']
        headers = {
            'X-Cisco-Meraki-API-Key': meraki_api_key,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        get_alert_profile = requests.get(url, headers=headers, verify=False)
        response = get_alert_profile.json()
        sensorlist_putrequest = response['serials']
        for sensor in ap_to_snooze['snoozed_sensors']:
            sensorlist_putrequest.append(sensor)
        data = {
            'name': response['name'],
            'scheduleId': response['scheduleId'],
            'conditions': response['conditions'],
            'recipients': response['recipients'],
            'serials': sensorlist_putrequest
        }
        put_alert_profile = requests.put(url, headers=headers, data=json.dumps(data), verify=False)
        print(put_alert_profile)


@app.route('/submit_sensor', methods=['GET', 'POST'])
def submit_sensor():
    global alert_profiles
    global alert_profiles_overview
    global sensor

    req = request.form
    sensor_alertprofile_string = list(req.keys())[0]
    sensor_alertprofile_list = sensor_alertprofile_string.split('...')
    sensor_alertprofile_dict = {
        'sensor': sensor_alertprofile_list[0],
        'alertprofile': sensor_alertprofile_list[1],
        'change': sensor_alertprofile_list[2]
    }

    serial = []
    for sen in sensor_mapping:
        if sensor_alertprofile_dict['sensor'] == 'all':
            serial.append(sen['serial'])
            dict_alerts = alert_profiles_overview
        else:
            if sen['name'] == sensor_alertprofile_dict['sensor']:
                serial.append(sen['serial'])
            dict_alerts = alert_profiles

    headers = {
        'X-Cisco-Meraki-API-Key': meraki_api_key,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    for ale in dict_alerts:
        if ale['name'] == sensor_alertprofile_dict['alertprofile']:
            alertprofile_id = ale['id']
            url = 'https://api.meraki.com/api/v1/networks/' + network_id + '/sensors/alerts/profiles/' + alertprofile_id
            get_alert_profile = requests.get(url, headers=headers, verify=False)
            response = get_alert_profile.json()
            sensorlist_putrequest = response['serials']
            if sensor_alertprofile_dict['change'] == 'assign':
                for s in serial:
                    if s not in sensorlist_putrequest:
                        sensorlist_putrequest.append(s)
            elif sensor_alertprofile_dict['change'] == 'unassign':
                for s in serial:
                    if s in sensorlist_putrequest:
                        sensorlist_putrequest.remove(s)
            data = {
                'name': response['name'],
                'scheduleId': response['scheduleId'],
                'conditions': response['conditions'],
                'recipients': response['recipients'],
                'serials': sensorlist_putrequest
            }
            put_alert_profile = requests.put(url, headers=headers, data=json.dumps(data), verify=False)
            print(put_alert_profile)

    return redirect(url_for('.heatmap', sensor=sensor))


@app.route('/add_alertprofile', methods=['GET', 'POST'])
def add_alertprofile():
    req = request.form
    sensor_name = request.args.get('sensor')

    if sensor_name == "all":
        try:
            if req["ap_sensorapply_all"] == "on":
                serial = []
                for s in sensor_mapping:
                    serial.append(s['serial'])
        except:
            serial = []

        conditions = []
        condition_typ = req["ap_conditiontype_all"]
        if condition_typ == "temperature":
            try:
                c = {
                    "type": condition_typ,
                    "unit": "celsius",
                    "disabled": False,
                    "direction": "+",
                    "threshold": int(req["above_t_value_all"])
                }

                if req["above_t_time_all"] != "any":
                    duration = int(req["above_t_time_all"]) * 60
                    c['duration'] = duration
                conditions.append(c)
            except Exception as e:
                print(e)

            try:
                c = {
                    "type": condition_typ,
                    "unit": "celsius",
                    "disabled": False,
                    "direction": "-",
                    "threshold": int(req["below_t_value_all"])
                }
                if req["below_t_time_all"] != "any":
                    duration = int(req["below_t_time_all"]) * 60
                    c['duration'] = duration
                conditions.append(c)

            except Exception as e:
                print(e)

        elif condition_typ == "humidity":
            try:
                c = {
                    "type": condition_typ,
                    "disabled": False,
                    "direction": "+",
                    "threshold": int(req["above_h_value_all"])
                }
                if req["above_h_time_all"] != "any":
                    duration = int(req["above_h_time_all"]) * 60
                    c['duration'] = duration
                conditions.append(c)

            except:
                print("Error with Humidity sensor")

            try:
                c = {
                    "type": condition_typ,
                    "disabled": False,
                    "direction": "-",
                    "threshold": int(req["below_h_value_all"])
                }
                if req["below_h_time_all"] != "any":
                    duration = int(req["below_h_time_all"]) * 60
                    c['duration'] = duration
                conditions.append(c)

            except:
                print("Error with humidity sensor")

        elif condition_typ == "water_detection":
            c = {
                "type": condition_typ,
                "disabled": False,
                "direction": "+",
                "threshold": 1
            }
            conditions.append(c)

        elif condition_typ == "door":
            c = {
                "type": condition_typ,
                "disabled": False,
                "duration": 0,
                "direction": "+",
                "threshold": 1,
                "disabledDuration": True
            }
            conditions.append(c)

        data = {
            "name": req["ap_name_all"],
            "scheduleId": "",
            "conditions": conditions,
            "recipients": {
                "emails": [],
                "smsNumbers": [],
                "httpServerIds": []
            },
            "serials": serial
        }

    else:
        try:
            if req["ap_sensorapply"] == "on":
                serial = []
                for s in sensor_mapping:
                    if sensor_name == s['name']:
                        serial.append(s['serial'])
        except:
            serial = []

        conditions = []
        condition_typ = req["ap_conditiontype"]
        if condition_typ == "temperature":
            try:
                c = {
                    "type": condition_typ,
                    "unit": "celsius",
                    "disabled": False,
                    "direction": "+",
                    "threshold": int(req["above_t_value"])
                }
                if req["above_t_time"] != "any":
                    duration = int(req["above_t_time"]) * 60
                    c['duration'] = duration
                conditions.append(c)
            except:
                print("Error with temperature sensor")

            try:
                c = {
                    "type": condition_typ,
                    "unit": "celsius",
                    "disabled": False,
                    "direction": "-",
                    "threshold": int(req["below_t_value"])
                }
                if req["below_t_time"] != "any":
                    duration = int(req["below_t_time"]) * 60
                    c['duration'] = duration
                conditions.append(c)
            except:
                print("Error with Temperature sensor")

        elif condition_typ == "humidity":
            try:
                c = {
                    "type": condition_typ,
                    "disabled": False,
                    "direction": "+",
                    "threshold": int(req["above_h_value"])
                }
                if req["above_h_time"] != "any":
                    duration = int(req["above_h_time"]) * 60
                    c['duration'] = duration
                conditions.append(c)
            except:
                print("Error with humidity sensor")

            try:
                c = {
                    "type": condition_typ,
                    "disabled": False,
                    "direction": "-",
                    "threshold": int(req["below_h_value"])
                }
                if req["below_h_time"] != "any":
                    duration = int(req["below_h_time"]) * 60
                    c['duration'] = duration
                conditions.append(c)
            except:
                print("Error with humifity sensor")

        elif condition_typ == "water_detection":
            c = {
                "type": condition_typ,
                "disabled": False,
                "direction": "+",
                "threshold": 1
            }
            conditions.append(c)

        elif condition_typ == "door":
            c = {
                "type": condition_typ,
                "disabled": False,
                "duration": 0,
                "direction": "+",
                "threshold": 1,
                "disabledDuration": True
            }
            conditions.append(c)

        data = {
            "name": req["ap_name"],
            "scheduleId": "",
            "conditions": conditions,
            "recipients": {
                "emails": [],
                "smsNumbers": [],
                "httpServerIds": []
            },
            "serials": serial
        }

    # add alert profile
    url = "https://api.meraki.com/api/v1/networks/" + network_id + "/sensors/alerts/profiles"
    headers = {
        'X-Cisco-Meraki-API-Key': meraki_api_key,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=json.dumps(data))
    print(response)
    return redirect(url_for('.heatmap', sensor=sensor_name))



@app.route('/grafana_chart', methods=['GET', 'POST'])
def grafana_chart():
    time_picker_tohours = {"Last hour" : 1,"Last 4 hours": 4, "Last 24 hours":24, "Last 2 days":48, "Last 7 days":168, "Last 30 days": 720, "Last 90 days": 2160}
    content = 'Grafana Chart'
    default_selected = "Last 7 days"

    if request.method == 'GET':
        end_tick = ticks(datetime.now())
        start_tick = ticks(datetime.now() + timedelta(hours=-time_picker_tohours[default_selected]))
        return render_template("grafana_import.html", content=content, times = [*time_picker_tohours], default_select=default_selected, start_tick = start_tick, end_tick = end_tick)
    else:
        selected = request.form.get('times', '')
        end_tick = ticks(datetime.now())
        start_tick = ticks(datetime.now() + timedelta(hours=-time_picker_tohours[selected]))
        return render_template("grafana_import.html", content=content, times = [*time_picker_tohours], default_select=selected, start_tick = start_tick, end_tick = end_tick)

def ticks(dt):
    return time.mktime(dt.timetuple()) * 1000

@app.route('/', methods=['GET', 'POST'])
def alert():
  flash(alerts())
  return render_template("start_page.html")


if __name__ == "__main__":
    app.run(port=5001, debug=True, threaded=True)
