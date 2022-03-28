import pandas as pd
import numpy as np
from config import sensor_mapping
from influxdb_client import InfluxDBClient
from config import org, token, bucket, influx_url, weather_location

import datetime
from average_temp import get_average_temp, format_date
from pylab import *
import matplotlib.pyplot as plt
from PIL import Image

from data_collector import get_historical_weather_reading

from meteostat import Point as meteoPoint, Hourly


client = InfluxDBClient(url=influx_url, token=token, org=org)
query_api = client.query_api()

#Observations
#Plot of the evolution of the inside average temperature during a week
def get_average_temp_over_last_days(n_days):
    temp_by_day=[]
    for i in range(n_days):
        start="-"+str(i+1)+"d0h0m0s"
        stop="-"+str(i)+"d0h0m0s"

        tables = query_api.query(f'from(bucket:"{bucket}")'
                                 f' |> range(start: {start},'
                                 f' stop:{stop})'
                                 f' |> filter(fn: (r) => r["_field"] == "temperature")'
                                 f' |> filter(fn: (r) => r["location"] == "L404")'
                                 f' |> yield(name: "mean")')

        values = {}
        for table in tables:
            for record in table.records:
                if (record.get_measurement() not in values):
                    values[record.get_measurement()] = record.get_value()

        data = list(values.values())
        mean = np.mean(data, axis=0)
        sd = np.std(data, axis=0)
        minTemp = mean - 0.5 * sd
        maxTemp = mean + 0.5 * sd
        final_data = [x for x in data if ((x > minTemp) & (x < maxTemp))]
        final_mean = np.mean(final_data)
        temp_by_day.append(final_mean)

    return temp_by_day


def get_outside_temp_over_last_days(ndays):
    temp_by_day =[]
    data=get_historical_weather_reading().reset_index(level=0)
    for i in range(ndays):
        date=str(datetime.datetime.now()-datetime.timedelta(days=i)).split(" ")[0]
        temp_of_day_i=[]
        for j in range(len(data)):
            if str(data.iloc[j,0]).split(" ")[0]==date:
                temp_of_day_i.append(float(data.iloc[j,1]))
        temp_by_day.append(np.average(np.array(temp_of_day_i)))
    return temp_by_day





def inside_outside_temp_evolution_plot():
    fig,ax=plt.subplots()
    ax.plot(days, inside_temp_by_days, color='red', marker='o')
    ax.plot(days, outside_temp_by_days, color='blue', marker='o')
    ax.set_title('Average inside and outside temperature', fontsize=14)
    ax.set_xlabel('Date', fontsize=14)
    ax.set_xticks(days,rotation=25)
    ax.set_ylabel('Temperature ($^\circ$C)', fontsize=14)
    ax.legend(["Inside temp","Outside temp"])
    ax.grid(True)
    plt.gca().yaxis.set_major_formatter(mticker.FormatStrFormatter('%.1f'))
    plt.gca().xaxis.set_major_formatter(mdate.DateFormatter('%m-%d'))
    plt.savefig('./static/assets/img/energy_savings/inside_outside_temp.png')



#Plot of the difference of degrees between inside and outside temperature during the week
def dif_inside_outside_temp():
    fig,ax=plt.subplots()
    ax.plot(days, dif, color='green', marker='o')
    ax.set_title('Difference of degrees between \nthe inside and outside temperature', fontsize=14)
    ax.set_xlabel('Date', fontsize=14)
    ax.set_xticks(days,rotation=25)
    ax.set_ylabel('Difference in degrees Celsius', fontsize=14)
    ax.grid(True)
    plt.savefig('./static/assets/img/energy_savings/dif_inside_outside_temp.png')



def energy_consumption_by_days():
    fig,ax=plt.subplots()
    ax.plot(days, consumption, color='brown', marker='o')
    ax.set_title('Daily Estimated consumption ', fontsize=14)
    ax.set_xlabel('Date', fontsize=14)
    ax.set_xticks(days,rotation=25)
    ax.set_ylabel('Consumption(kwh)', fontsize=14)
    ax.grid(True)
    plt.gca().xaxis.set_major_formatter(mdate.DateFormatter('%m-%d')
    plt.savefig('./static/assets/img/energy_savings/estimated_consumption.png')



def compute_energy_expenses_over_week():
    sum =np.sum(consumption)
    return convert_energy_money(sum)



#Computing the estimated energy consumption over a week according to the difference of degrees between inside and outside

average_daily_consumption =18.74
average_temp_outside=11.7 #in the area of the office
average_temp_inside= 24
#Computing coef:
X = average_daily_consumption/abs(average_temp_inside - average_temp_outside)

#input : difference of degrees between inside and outside
#output : energy consumption in kwh over a day
def consumption_computing(inside, outside) :
	return abs(inside-outside)*X

#Convert the energy in kwh to money in €
def convert_energy_money(energy):
    return round(energy*0.256*1.2,2)

def convert_energy_money_np(energy):
    return np.around(energy*0.256*1.2,2)



days_to_plot=7
optimum_temp=23
inside_temp_by_days= get_average_temp_over_last_days(days_to_plot)[::-1]
days = [str(datetime.datetime.now()-datetime.timedelta(days=i)).split(" ")[0] for i in range(days_to_plot)][::-1]
outside_temp_by_days =get_outside_temp_over_last_days(days_to_plot)[::-1]
consumption=consumption_computing(np.array(inside_temp_by_days),np.array(outside_temp_by_days))
dif=np.array(inside_temp_by_days) -np.array(outside_temp_by_days)
temp_inside_average=np.average(inside_temp_by_days)
temp_outside_average =np.average(outside_temp_by_days)
consumption_average=np.average(consumption)
#Recommendations :
def compute_dif_temp(temp):

    return temp_average-temp

def compute_energy_savings(temp,outside ):
    energy = consumption_computing(temp, outside)
    return consumption_average- energy

dif_temp_reco = np.array([temp_inside_average-i for i in range(5)])
energy_savings =[]
for i in range(5) :
    energy_savings.append(compute_energy_savings(temp_inside_average-i,temp_outside_average))


money_savings=convert_energy_money_np(np.array(energy_savings))

def compute_optimum_reduction():
    return round(temp_inside_average -optimum_temp,1)

def plot_energy_savings_by_temp():
    fig,ax=plt.subplots()
    ax.plot([-i for i in range(5)], energy_savings, color='g', marker='o')
    ax.set_title('Estimated energy savings by degrees decreased in the room', fontsize=14)
    ax.set_xlabel('Temperature reduction ($^\circ$C)', fontsize=14)
    ax.set_xticks([-i for i in range(5)],rotation=25)
    ax.set_ylabel('Weekly Energy savings(kwh)', fontsize=14)
    ax.grid(True)
    plt.savefig('./static/assets/img/energy_savings/estimated_energy_savings.png')



def plot_money_saved_by_temp():
    fig,ax=plt.subplots()
    ax.plot([-i for i in range(5)], money_savings, color='g', marker='o')
    ax.set_title('Estimated energy savings by degrees decreased in the room', fontsize=14)
    ax.set_xlabel('Temperature reduction ($^\circ$C)', fontsize=14)
    ax.set_xticks([-i for i in range(5)], rotation=25)
    ax.set_ylabel('Weekly Money Saving(euro)', fontsize=14)
    ax.grid(True)
    plt.savefig('./static/assets/img/energy_savings/estimated_money_savings.png')



def get_energy_infos():
    #dif_inside_outside_temp()
    inside_outside_temp_evolution_plot()
    energy_consumption_by_days()
    weekly_energy_expenses = compute_energy_expenses_over_week()
    plot_energy_savings_by_temp()
    plot_money_saved_by_temp()
    optimum_reduction = compute_optimum_reduction()
    return optimum_reduction, weekly_energy_expenses
"""
if (__name__ == "__main__"):
    print("Obervations : ")
    dif_inside_outside_temp()
    inside_outside_temp_evolution_plot()
    energy_consumption_by_days()
    print("We estimate in the last 7 days that you spent ",compute_energy_expenses_over_week(),"€ for the temperature regulation in your room")

    print("Recommendations : ")
    plot_energy_savings_by_temp()
    plot_money_saved_by_temp()
    print("The optimum temperature in an office is ",optimum_temp,"°C so we advice you to change the temperature by ",compute_optimum_reduction(),"°C")
"""