from datetime import datetime, timedelta
from average_temp import get_average_temp, get_average_hum, get_latest_reading

def alerts():
    now = datetime.today() + timedelta(hours=-10)
    all_temp = get_latest_reading(now, 'temperature')
    avg_temp = get_average_temp(now)
    avg_humidity = get_average_hum(now)

    str_to_return = "all good"
    if avg_temp>30:
        str_to_return = 'Temperature of the room is too high'
    elif avg_temp < 20.5:
        str_to_return = 'Temperature too low'
    elif avg_temp > 26 and all_temp['12']>30.0 & all_temp['8']>30.0:
        str_to_return = 'Lower radiators temperature to save energy'
    elif avg_humidity<20:
        str_to_return = "Average humidity of the room is %d please check for any leak(AC,open window...)"%avg_humidity
    elif avg_temp<22 and all_temp['6']<20.0 & all_temp['7']<20.0 & all_temp['8']<20.0:
        str_to_return = "To save energy please turn off AC"
    
    return str_to_return

if (__name__ == "__main__"):
    alerts()