# ================================= #
#          Meraki Settings          #
# ================================= #

base_url = "https://api.meraki.com/api/v1"
meraki_api_key = "4cad7b04e58fba06aacd0e85d3230758a72894d3"
network_id = "L_660340295363203930" # this is the network id, found it on https://api.meraki.com/api/v1/organizations/660340295363199933/networks, where 660340295363199933 is the orgid

# serial numbers of your sensors
# example ["Q3CA-TFU4-A8QR","Q3CA-9EGL-8LQJ"] or leave empty []
temperature_sensors = ["Q3CA-TFU4-A8QR","Q3CA-9EGL-8LQJ"]


# ================================= #
#          INFLUX DB                #
# ================================= #

org = "merakiOrganization"
bucket = "merakiBucket"
token = "mGt4-g4XrPeZC1hfO4IMWi_9fTx4groCBjODkrtN6428E6vpaaRxJnvo3tkvA6dfJHc-nAb-IXrFB_x56C8y-g=="
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
        "name": "16",
        "serial": "Q3CA-TFU4-A8QR",
        "type": "temperature"
    },
    {
        "name": "15",
        "serial": "Q3CA-9EGL-8LQJ",
        "type": "temperature"
    }
]
