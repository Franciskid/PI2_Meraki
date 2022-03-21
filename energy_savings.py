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

#Observations
#Plot of the evolution of the inside average temperature during a week

#Plot of the evolution of the outside average temperature during a week

#Plot of the difference of degrees between inside and outside temperature during the week

#Computing the estimated energy consumption over a week according to the difference of degrees between inside and outside

#Converting this amount into money expenses  :

#Recommendations :
