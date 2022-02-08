# ================================= #
#          Meraki Settings          #
# ================================= #

base_url = "https://api.meraki.com/api/v1"
meraki_api_key = "4e8c23a94107f8882f2844b1b6fa87ab1d476ccd"
network_id = "L_660340295363203930"  # found it on https://api.meraki.com/api/v1/organizations/660340295363199933/networks, where 660340295363199933 is the orgid
floor_plan="g_660340295363201359"

# serial numbers of the sensors, all in name order. Not used anymore.
temperature_sensors = ["Q3CA-W7P5-GLWJ", "Q3CA-SPYL-SC5M", "Q3CA-T9FH-7ZF5", 
"Q3CA-3ZRV-MNTQ", "Q3CA-RR4K-8RYS", "Q3CA-K9TR-RE3G", 
"Q3CA-5D77-ZYLZ", "Q3CA-4ZSY-VW9J", "Q3CA-HCXU-CYW7", 
"Q3CA-KSP5-CGW3", "Q3CA-7CBZ-S875", "Q3CA-DW94-Q3XA",
"Q3CA-Y4FD-TEM9", "Q3CA-3Q5F-ZL2T", "Q3CA-9EGL-8LQJ",  
"Q3CA-TFU4-A8QR", "Q3CA-3Y93-LACF"]
door_sensors = ["Q3CC-CHNP-XUTA", "Q3CC-7QPS-TABH"]

# ================================= #
#          INFLUX DB                #
# ================================= #

org = "merakiOrganization"
bucket = "merakiBucket"
token = "LZoZzBICm4BG9NgMm-j5DwZsK5Uf1RHWgKLueSXghtd_emBlXbYmcERKHgJkVaSfnpF2h6sJUduxjtc8RP29yQ=="
influx_url = "http://localhost:8086"


# ================================= #
#      ASHRAE SETTINGS              #
# ================================= #

ASHRAE_low = 15
ASHRAE_high = 27

#Not used anymore.
# ================================= #
#       SENSOR MAPPINGS             #
# ================================= #

sensor_mapping = [
    {
        "name": "1",
        "serial": "Q3CA-W7P5-GLWJ",
        "type": "temperature"
    },
    {
        "name": "2",
        "serial": "Q3CA-SPYL-SC5M",
        "type": "temperature"
    },
    {
        "name": "3",
        "serial": "Q3CA-T9FH-7ZF5",
        "type": "temperature"
    },
    {
        "name": "4",
        "serial": "Q3CA-3ZRV-MNTQ",
        "type": "temperature"
    },
    {
        "name": "5",
        "serial": "Q3CA-RR4K-8RYS",
        "type": "temperature"
    },
    {
        "name": "6",
        "serial": "Q3CA-K9TR-RE3G",
        "type": "temperature"
    },
    {
        "name": "7",
        "serial": "Q3CA-5D77-ZYLZ",
        "type": "temperature"
    },
    {
        "name": "8",
        "serial": "Q3CA-4ZSY-VW9J",
        "type": "temperature"
    },
    {
        "name": "9",
        "serial": "Q3CA-HCXU-CYW7",
        "type": "temperature"
    },
    {
        "name": "10",
        "serial": "Q3CA-KSP5-CGW3",
        "type": "temperature"
    },
    {
        "name": "11",
        "serial": "Q3CA-7CBZ-S875",
        "type": "temperature"
    },
    {
        "name": "12",
        "serial": "Q3CA-DW94-Q3XA",
        "type": "temperature"
    },
    {
        "name": "13",
        "serial": "Q3CA-Y4FD-TEM9",
        "type": "temperature"
    },
    {
        "name": "14",
        "serial": "Q3CA-3Q5F-ZL2T",
        "type": "temperature"
    },
    {
        "name": "15",
        "serial": "Q3CA-9EGL-8LQJ",
        "type": "temperature"
    },
    {
        "name": "16",
        "serial": "Q3CA-TFU4-A8QR",
        "type": "temperature"
    },
    {
        "name": "17",
        "serial": "Q3CA-3Y93-LACF",
        "type": "temperature"
    },
    {
        "name": "Left door",
        "serial": "Q3CC-CHNP-XUTA",
        "type": "door"
    },
    {
        "name": "Right door",
        "serial": "Q3CC-7QPS-TABH",
        "type": "door"
    }
]

# ================================= #
#         Weather Point             #
# ================================= #

#Weather location from Courbevoie => closest weather metrics are taken from Paris
weather_location = {"lat" : 48.896640253127785, "lon" : 2.23684585029297, "alt" : 50}
