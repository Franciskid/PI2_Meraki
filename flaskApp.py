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

from config import (meraki_api_key, network_id,
                    sensor_mapping)
from config_sensors import get_sensors
from alert_profiles import alerts
from data_collector import get_latest_sensor_reading
from heatmap_creation import get_heatmap
from energy_savings import get_energy_infos, optimum_temp

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


@app.route('/', methods=['GET'])
def index():
    flash(alerts())
    return render_template("start_page.html")


@app.route('/heatmap', methods=['GET', 'POST'])
def heatmap():
    automatic_threshold = False if request.form.get("cb_automatic_threshold") else True
    min_threshold = -1 if automatic_threshold else request.form.get("min_temp_threshold", type=int)
    max_threshold = -1 if automatic_threshold else request.form.get("max_temp_threshold", type=int)
    min_threshold, max_threshold = min(min_threshold, max_threshold), max(min_threshold, max_threshold)

    date = datetime.now() if request.method == "GET" else datetime.strptime(request.form.get('time', ''), "%Y-%m-%dT%H:%M")

    t_min,t_max,gap = get_heatmap(date, min_threshold, max_threshold)

    return render_template("heatmap.html", time_chose=date.strftime("%Y-%m-%dT%H:%M"), automatic=automatic_threshold, min_threshold=min_threshold, max_threshold = max_threshold,
                           t_min=t_min,
                           t_max=t_max,
                           gap=gap)


@app.route('/energy_management', methods=["GET"])
def energy_management():
    optimum_reduction, weekly_energy_expenses,monthly_energy_saved=get_energy_infos()
    energy_expenses_sentence1 ="We estimate in the last 7 days that you spent "
    energy_expenses_sentence2=str(weekly_energy_expenses)+"€"
    energy_expenses_sentence3=" for the temperature regulation in your room."
    optimum_reduction_sentence1 =str("The optimum temperature in an office is "+str(optimum_temp)+"°C so we advise you to change the temperature by ")
    optimum_reduction_sentence2 =str(optimum_reduction)+"°C"

    return render_template("energy_management.html", weekly_energy_expenses1=energy_expenses_sentence1,
                                                     weekly_energy_expenses2=energy_expenses_sentence2,
                                                     weekly_energy_expenses3=energy_expenses_sentence3,
                                                     optimum_reduction1=optimum_reduction_sentence1,
                                                     optimum_reduction2=optimum_reduction_sentence2,
                                                     monthly_energy_saved=str(monthly_energy_saved)+"€",
                                                     content = "Energy Management")


@app.route('/grafana_chart', methods=['GET', 'POST'])
def grafana_chart():
    time_picker_tohours = {"Last hour" : 1,"Last 4 hours": 4, "Last 24 hours":24, "Last 2 days":48, "Last 7 days":168, "Last 30 days": 720, "Last 90 days": 2160}
    content = 'Grafana Chart'
    selected = "Last 7 days" if request.method == 'GET' else request.form.get('times', '')

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
