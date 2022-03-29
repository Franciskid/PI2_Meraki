# PI² Project! 
<img src="https://www.esilv.fr/ecole-ingenieur/logos/logo_esilv_png_couleur.png" width="100"> <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Meraki_Logo_2016.svg/800px-Meraki_Logo_2016.svg.png" height="100">

Our project's goal, made in collaboration with Cisco Meraki, is to reduce the **carbon footprint** and **energy consumption** in **datacenters** and **offices** by processing data from Meraki sensors.

Original code from [github:gve_devnet_meraki_mt_dashboard](https://github.com/gve-sw/gve_devnet_meraki_mt_dashboard), modified for our project's needs
# Contacts
- BOUCHELLEGHEM Syrine
- COUTAU François
- NAVARRE Quentin
- SHI Jianrui
## Solution Components

-   Docker
    -   Grafana
    -   Influx DB
-   Python 3.8
-   Cisco Meraki sensors
    -   [API Documentation](https://developer.cisco.com/meraki/api-v1/)

##  Setup

1.  Clone the repository.
    
    ```
    git clone (repo)
    
    ```
    
2.  Open the `config.py` file. Fill in the following information:
    
    ```
     network_id = " "
    
     SENSOR_MAPPING = [
         {
             "name": "", # name of the sensor
             "serial": "", # serial number of the sensor
             "type": "", # type of sensor, e.g. temperature/door
             "coordinates" : { # coordinate of the sensor, necessary for the heatmap
		             "x": 0,
		             "y": 0,
		             "z": 0
		     }
         } # copy this dictionary for as many sensors there are
     ]
    
    
    ```
#### Grafana and Influx DB Setup
4.  Go to the directory where the `docker-compose.yml` file is located, pull and build all images of the container:
    
    ```
     docker-compose build
    
    ```
    
5.  Start the containers in the background (-d). Grafana and InfluxDB will be automatically configured.
    
    ```
     docker-compose up -d
    
    ```
    
6.  Setup Influx DB. Go to "[http://localhost:8086/](http://localhost:8086/)" and enter the username, password, organization and bucket information.
    
7.  Get your Influx DB token from [http://localhost:8086/orgs/{org_id}/load-data/token](http://localhost:8086/orgs/%7Borg_id%7D/load-data/token) (Data --> Tokens).
    
8.  Login to your Grafana Dashboard from [http://localhost:3000/login](http://localhost:3000/login). Enter the username/password(admin/admin). You will be required to set a new password.
    

#### Web app Setup

9.  Add your Influx db token to Grafana datasources (Datasources --> InfluxDB --> token). Click Save&Test to check if your Influx DB and Grafana Dashboard are connected.

#### Tokens setup
10. Create a file called token_file.py in the main directory and put your tokens in it
```
meraki_api_key = ""
influx_token = ""
```
### Last steps
11.  Go to your app folder and install the libaries for the app code.
```
pip install -m requirements.txt
```
12.  Go to you Grafana dashboard and get URL link to add the grafana tables to the web app . The URL link can be found at: Dashboard --> Share Dashboard or Panel --> Link URL
    
13.  Add the link url to templates/grafana.html file
    
14.  Run the meraki_connector file to add data in your Influx DB Bucket.
```
 python data_collector.py
```
15.  Run your web application:
```
 python flaskApp.py
```
# Screenshots

![index](https://user-images.githubusercontent.com/74976008/160583940-10652f32-28ec-4314-b77e-93f64f74eff2.png)
![heatmap](https://user-images.githubusercontent.com/74976008/160633439-3a2c2b0d-95d8-41c9-a801-7aa5170389e6.png)
![grafana](https://user-images.githubusercontent.com/74976008/160633460-d8b27181-0103-4224-b231-6cdfb71b65af.png)
![energy](https://user-images.githubusercontent.com/74976008/160584066-0a37dca9-efbc-44dd-89ce-4d9291c9500a.png)

