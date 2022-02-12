import pandas as pd
import numpy as np
from config import sensor_mapping



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
def AssignTemperature(date):
    print(temp)

#Compute the distance between 2 points in 3d
def computeDistance(x_sensor,y_sensor, z_sensor, x,y,z):
    return pow(pow(x_sensor-x,2)+pow(y_sensor-y,2)+pow(z_sensor-z,2),1/2)

#Estimate the temperature of a sensor
def estimatedTemp(x,y,z):
    temp = 0
    sum_distance=0
    for i in range(len(df_sensors)):
        distance = computeDistance(df_sensors.iloc[i,1],df_sensors.iloc[i,2],df_sensors.iloc[i,3], x,y,z)
        temp+=distance * df_sensors.iloc[i,4]
        sum_distance+=distance

    point_temperature = temp/sum_distance
    return point_temperature

    
#Generate points between sensors to complete the heatmap
#These points are generated at regular intervals
def generatesPoints(npoints):
    df_heatmap=df_sensors.copy()

    volume = (max_x -min_x)*(max_y - min_y)*(max_z-min_z)
    interval = pow(volume/npoints, 1/3)

    for x in range(min_x,max_x,interval):
        for y in range(min_y, max_y,interval):
            for z in range(min_z,max_z,interval):
                df_heatmap.append({"name"="generated_point","x":x,"y":y,"z":z,"temperature":estimatedTemp(x,y,z)}, ignore_index=True)




df_heatmap=pd.DataFrame()
df_sensors=dataframe_creation()

min_x=df_sensors["x"].min()
min_y=df_sensors["y"].min()
min_z=df_sensors["z"].min()
max_x=df_sensors["x"].max()
max_y=df_sensors["y"].max()
max_z=df_sensors["z"].max()

if __name__=="__main__":

    print(df.head(20))
