from token_file import meraki_api_key, influx_token

# ================================= #
#          Meraki Settings          #
# ================================= #

base_url = "https://api.meraki.com/api/v1"
meraki_api_key = meraki_api_key
network_id = "L_660340295363203930"  # found it on https://api.meraki.com/api/v1/organizations/660340295363199933/networks, where 660340295363199933 is the orgid

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
token = influx_token
influx_url = "http://localhost:8086"


# ================================= #
#      ASHRAE SETTINGS              #
# ================================= #

ASHRAE_low = 15
ASHRAE_high = 27

# ================================= #
#       SENSOR MAPPINGS             #
# ================================= #

sensor_mapping = [
    {
        "name": "1",
        "serial": "Q3CA-W7P5-GLWJ",
        "type": "temperature",
        "coordinates" : {
            "x":0,
            "y":565,
            "z":230
        }
    },
    {
        "name": "2",
        "serial": "Q3CA-SPYL-SC5M",
        "type": "temperature",
        "coordinates" : {
            "x":0,
            "y":287,
            "z":230
        }
    },
    {
        "name": "3",
        "serial": "Q3CA-T9FH-7ZF5",
        "type": "temperature",
        "coordinates" : {
            "x":1065,
            "y":272,
            "z":230
        }
    },
    {
        "name": "4",
        "serial": "Q3CA-3ZRV-MNTQ",
        "type": "temperature",
        "coordinates" : {
            "x":1065,
            "y":570,
            "z":230
        }
    },
    {
        "name": "5",
        "serial": "Q3CA-RR4K-8RYS",
        "type": "temperature",
        "coordinates" : {
            "x":252,
            "y":285,
            "z":109
        }
    },
    {
        "name": "6",
        "serial": "Q3CA-K9TR-RE3G",
        "type": "temperature",
        "coordinates" : {
            "x":264,
            "y":94,
            "z":240
        }
    },
    {
        "name": "7",
        "serial": "Q3CA-5D77-ZYLZ",
        "type": "temperature",
        "coordinates" : {
            "x":0,
            "y":565,
            "z":230
        }
    },
    {
        "name": "8",
        "serial": "Q3CA-4ZSY-VW9J",
        "type": "temperature",
        "coordinates" : {
            "x":464,
            "y":94,
            "z":240
        }
    },
    {
        "name": "9",
        "serial": "Q3CA-HCXU-CYW7",
        "type": "temperature",
        "coordinates" : {
            "x":86,
            "y":709,
            "z":38
        }
    },
    {
        "name": "10",
        "serial": "Q3CA-KSP5-CGW3",
        "type": "temperature",
        "coordinates" : {
            "x":485,
            "y":428,
            "z":38
        }
    },
    {
        "name": "11",
        "serial": "Q3CA-7CBZ-S875",
        "type": "temperature",
        "coordinates" : {
            "x":705,
            "y":175,
            "z":116
        }
    },
    {
        "name": "12",
        "serial": "Q3CA-DW94-Q3XA",
        "type": "temperature",
        "coordinates" : {
            "x":709,
            "y":668,
            "z":87
        }
    },
    {
        "name": "13",
        "serial": "Q3CA-Y4FD-TEM9",
        "type": "temperature",
        "coordinates" : {
            "x":1004,
            "y":648,
            "z":32
        }
    },
    {
        "name": "14",
        "serial": "Q3CA-3Q5F-ZL2T",
        "type": "temperature",
        "coordinates" : {
            "x":668,
            "y":455,
            "z":109
        }
    },
    {
        "name": "15",
        "serial": "Q3CA-9EGL-8LQJ",
        "type": "temperature",
        "coordinates" : {
            "x":229,
            "y":699,
            "z":220
        }
    },
    {
        "name": "16",
        "serial": "Q3CA-TFU4-A8QR",
        "type": "temperature",
        "coordinates" : {
            "x":951,
            "y":651,
            "z":187
        }
    },
    {
        "name": "17",
        "serial": "Q3CA-3Y93-LACF",
        "type": "temperature",
        "coordinates" : {
            "x":468,
            "y":683,
            "z":187
        }
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
