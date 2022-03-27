from datetime import datetime, timedelta, date
from average_temp import get_average_temp, get_average_hum, get_latest_reading

def alerts():
    now = datetime.today() + timedelta(hours=-10)
    all_temp = get_latest_reading(now, 'temperature')
    avg_temp = get_average_temp(now)
    avg_humidity = get_average_hum(now)

    status = f"Current temperature is {'{:.1f}'.format(avg_temp)}°C. Curent humidity is {'{:.1f}'.format(avg_humidity)}%."
    str_to_return = f"EVERYTHING IS FINE ! {status}  \n\tThey are within the expected range for the current season !"
    season = get_season(date.today())
    if (avg_temp > 25.5 and season == 'summer') or (avg_temp > 23.5 and season == 'winter'):
        temp = 25.5 if season == "summer" else 23.5
        str_to_return = f'Temperature of the room is too high ! {status} You should reduce that to {temp}°C'
    elif (avg_temp < 23 and season == 'summer') or (avg_temp < 20 and season == 'winter'):
        temp = 23 if season == "summer" else 20
        str_to_return = f'Temperature of the room is too low ! {status} You should increase that to {temp}°C'
    elif avg_temp > 26 and all_temp['12']>30.0 and all_temp['8']>30.0:
        str_to_return = f'Lower radiators temperature to save energy {status} ' 
    elif avg_humidity<20:
        str_to_return = f"Average humidity of the room is %d please check for any leak(AC,open window...)"%avg_humidity
    elif avg_temp<22 and all_temp['6']<20.0 and all_temp['7']<20.0 and all_temp['8']<20.0:
        str_to_return = f"To save energy please turn off AC {status} "
    
    return str_to_return

Y = 2022 # dummy leap year to allow input X-02-29 (leap day)
seasons = [('winter', (date(Y,  1,  1),  date(Y,  6, 20))),
           ('summer', (date(Y,  6, 21),  date(Y, 12, 20))),
           ('winter', (date(Y, 12, 21),  date(Y, 12, 31)))]

def get_season(now):
    if isinstance(now, datetime):
        now = now.date()
    now = now.replace(year=Y)
    return next(season for season, (start, end) in seasons
                if start <= now <= end)



if (__name__ == "__main__"):
    alerts()