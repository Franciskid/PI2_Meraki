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
import io
from PIL import Image


client = InfluxDBClient(url=influx_url, token=token, org=org)
query_api = client.query_api()

def GetTemperature(date=datetime.today() + timedelta(hours=-0.5)):
    start = datetime.today() - date
    stop = (datetime.today() + timedelta(hours=1)) - date
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
        if z !=None :
            distance = computeDistance(df_sensors.iloc[i,1],df_sensors.iloc[i,2],df_sensors.iloc[i,3], x,y,z)
        else :
            distance=computeDistance(df_sensors.iloc[i,1],df_sensors.iloc[i,2],0,x,y,0)
        temp+=pow(1/distance,power) * df_sensors.iloc[i,4]
        sum_distance+=pow(1/distance,power)

    point_temperature = temp/sum_distance
    return point_temperature

def format_date(td):
    return f'{td.days}d{td.seconds//3600}h{(td.seconds//60)%60}m{td.seconds % 60}s'

#Generate points between sensors to complete the heatmap
#These points are generated at regular intervals
def generatesPoints3D(npoints):
    df_heatmap=df_sensors.copy()

    volume = (max_x -min_x)*(max_y - min_y)*(max_z-min_z)
    interval = int(pow(volume/npoints, 1/3))

    for x in range(min_x,max_x,interval):
        for y in range(min_y, max_y,interval):
            for z in range(min_z,max_z,int(interval/2)):
                df_heatmap=df_heatmap.append({"name_sensor":"generated_point","x":x,"y":y,"z":z,"temperature":estimatedTemp(x,y,z,10)}, ignore_index=True)


    return df_heatmap

df_heatmap=pd.DataFrame()
df_sensors=dataframe_creation()
AssignTemperature()
df_sensors=df_sensors.dropna()

min_x=int(df_sensors["x"].min())
min_y=int(df_sensors["y"].min())
min_z=int(df_sensors["z"].min())
max_x=int(df_sensors["x"].max())
max_y=int(df_sensors["y"].max())
max_z=int(df_sensors["z"].max())

def randrange(n, vmin, vmax):
    return (vmax-vmin)*np.random.rand(n) + vmin

def heatmap_2D(nbpoints):
    x,y=np.meshgrid(np.linspace(min_x,max_x,int(nbpoints**0.5)),np.linspace(min_y,max_y,int(nbpoints**0.5)))
    temp=estimatedTemp(x,y,None,4)
    temp_min, temp_max = -np.abs(temp).max(), np.abs(temp).max()

    img=Image.open("./IMAGES/floor plan.png")

    img=img.resize((int(max_x),int(max_y)),Image.ANTIALIAS)
    fig, ax = plt.subplots()

    c = ax.pcolormesh(x, y, temp, cmap='coolwarm', alpha=0.5)
    ax.set_title('2D Top view')
    # set the limits of the plot to the limits of the data
    ax.axis([x.min(), x.max(), y.min(), y.max()])
    fig.colorbar(c, ax=ax)
    ax.imshow(img)
    ax.set_xlabel('X coordinates (cm)')
    ax.set_ylabel('Y coordinates (cm)')

    plt.savefig('./static/assets/img/2dHeatmap.png')


    img=Image.open("./static/assets/img/2dHeatmap.png")
    img=img.resize((800,600),Image.ANTIALIAS)
    img.save("./static/assets/img/2dHeatmap.png")


def heatmap_3D(df):
    fig = plt.figure(figsize=(8,6))

    ax = fig.add_subplot(111,projection='3d')


    xs = df["x"].tolist()
    ys = df["y"].tolist()
    zs = df["z"].tolist()
    temperature= df["temperature"].tolist()


    colors = cm.coolwarm((np.asarray(temperature)-min(temperature))/((max(temperature)-min(temperature))))
    yg = ax.scatter(xs, ys, zs, c=colors, marker='o', alpha=0.05, s=2000)

    colmap = cm.ScalarMappable(cmap=cm.coolwarm)
    colmap.set_array(temperature)

    cb = fig.colorbar(colmap)


    ax.set_xlabel('X coordinates (cm)')
    ax.set_ylabel('Y coordinates (cm)')
    ax.set_zlabel('Z coordinates (cm)')
    ax.set_title('3D corner view')
    plt.savefig('./static/assets/img/3dHeatmap.png')



def get_heatmap():
    heatmap_3D(generatesPoints3D(300))
    heatmap_2D(100000)
    t_min =around(df_sensors["temperature"].min(),1)
    t_max=around(df_sensors["temperature"].max(),1)
    gap =around(t_max-t_min,1)
    return str(t_min)+"°C",str(t_max)+"°C",str(gap)+"°C"




if __name__=="__main__":
    get_heatmap()
