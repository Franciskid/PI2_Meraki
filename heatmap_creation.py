import pandas as pd
import numpy as np
from config import sensor_mapping
from influxdb_client import InfluxDBClient
from config import org, token, bucket, influx_url

from datetime import datetime, timedelta
from average_temp import get_average_temp
from pylab import *
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from datetime import datetime


client = InfluxDBClient(url=influx_url, token=token, org=org)
query_api = client.query_api()

def GetTemperature(date=datetime.today() + timedelta(hours=-0.5)):
    start = datetime.today() - date
    print(format_date(start))
    stop = (datetime.today() + timedelta(hours=1)) - date
    print(format_date(stop))
    tables = query_api.query(f'from(bucket: "{bucket}")'
                 f'|> range(start: -{format_date(stop)},'
                 f' stop: {format_date(start)})'
                 f'|> filter(fn: (r) => r["_field"] == "temperature")'
                 f'|> filter(fn: (r) => r["location"] == "L404")'
                 f'|> yield(name: "mean")')


    values = {}
    for table in tables:
        for record in table.records:
            if (record.get_measurement() not in values):
                values[record.get_measurement()] = record.get_value()



    return values

#Create a dataframe with thename the coordinates and the temperature of the sensors
def dataframe_creation():
    df= pd.DataFrame(columns=["name_sensor","x","y","z","temperature"])
    id=0
    for i in sensor_mapping :
        if i["type"]=="temperature":
            df.loc[id]=[i["name"],i["coordinates"]["x"],i["coordinates"]["y"],i["coordinates"]["z"], 0]
            id+=1
    return df

#Put temperature of the sensors in the df
def AssignTemperature():
    average_temp =get_average_temp(datetime.today())
    print(average_temp)
    temp=GetTemperature()


    for i in range(len(df_sensors)):
        if str(i+1) in temp :
            df_sensors.iloc[i,4]=temp[str(i+1)]
        else :
            df_sensors.iloc[i,4]=average_temp


#Compute the distance between 2 points in 3d
def computeDistance(x_sensor,y_sensor, z_sensor, x,y,z):
    return pow(pow(x_sensor-x,2)+pow(y_sensor-y,2)+pow(z_sensor-z,2),1/2)

#Estimate the temperature of a sensor
def estimatedTemp(x,y,z,power):
    temp = 0
    sum_distance=0
    for i in range(len(df_sensors)):
        distance = computeDistance(df_sensors.iloc[i,1],df_sensors.iloc[i,2],df_sensors.iloc[i,3], x,y,z)
        temp+=pow(1/distance,power) * df_sensors.iloc[i,4]
        sum_distance+=pow(1/distance,power)

    point_temperature = temp/sum_distance
    return point_temperature

def format_date(td):
    return f'{td.days}d{td.seconds//3600}h{(td.seconds//60)%60}m{td.seconds % 60}s'
#Generate points between sensors to complete the heatmap
#These points are generated at regular intervals
def generatesPoints(npoints):
    df_heatmap=df_sensors.copy()

    volume = (max_x -min_x)*(max_y - min_y)*(max_z-min_z)
    interval = int(pow(volume/npoints, 1/3))

    for x in range(min_x,max_x,interval):
        for y in range(min_y, max_y,interval):
            for z in range(min_z,max_z,interval):
                df_heatmap=df_heatmap.append({"name_sensor":"generated_point","x":x,"y":y,"z":z,"temperature":estimatedTemp(x,y,z,15)}, ignore_index=True)



    return df_heatmap

df_heatmap=pd.DataFrame()
df_sensors=dataframe_creation()
AssignTemperature()

min_x=int(df_sensors["x"].min())
min_y=int(df_sensors["y"].min())
min_z=int(df_sensors["z"].min())
max_x=int(df_sensors["x"].max())
max_y=int(df_sensors["y"].max())
max_z=int(df_sensors["z"].max())

def randrange(n, vmin, vmax):
    return (vmax-vmin)*np.random.rand(n) + vmin

def heatmap_3D(df):
    fig = plt.figure(figsize=(8,6))

    ax = fig.add_subplot(111,projection='3d')


    xs = df["x"].tolist()
    ys = df["y"].tolist()
    zs = df["z"].tolist()
    temperature= df["temperature"].tolist()

    colors = cm.coolwarm(np.asarray(temperature)/max(temperature))



    colmap = cm.ScalarMappable(cmap=cm.coolwarm)
    colmap.set_array(temperature)

    yg = ax.scatter(xs, ys, zs, c=colors, marker='o', alpha=0.1, s=2000)
    cb = fig.colorbar(colmap)

    ax.set_xlabel('X Label')
    ax.set_ylabel('Y Label')
    ax.set_zlabel('Z Label')


    plt.show()

if __name__=="__main__":

    df_heatmap=generatesPoints(300)
    print(df_heatmap.head(25))
    heatmap_3D(df_heatmap)
