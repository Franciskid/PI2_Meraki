from datetime import datetime, timedelta, date
from average_temp import get_average_temp, get_average_hum, get_latest_reading

def alerts():
    now = datetime.today() + timedelta(hours=-10)
    all_temp = get_latest_reading(now, 'temperature')
    avg_temp = get_average_temp(now)
    avg_humidity = get_average_hum(now)

    str_to_return = "Temperatures are fine !"
    if (avg_temp > 25.5 and get_season(date.today()) == 'summer') or (avg_temp > 23.5 and get_season(date.today()) == 'winter'):
        str_to_return = 'Temperature of the room is too high !'
    elif (avg_temp < 23 and get_season(date.today()) == 'summer') or (avg_temp < 20 and get_season(date.today()) == 'winter'):
        str_to_return = 'Temperature of the room is too low !'
    elif avg_temp > 26 and all_temp['12']>30.0 & all_temp['8']>30.0:
        str_to_return = 'Lower radiators temperature to save energy'
    elif avg_humidity<20:
        str_to_return = "Average humidity of the room is %d please check for any leak(AC,open window...)"%avg_humidity
    elif avg_temp<22 and all_temp['6']<20.0 & all_temp['7']<20.0 & all_temp['8']<20.0:
        str_to_return = "To save energy please turn off AC"
    
    return str_to_return

Y = 2022 # dummy leap year to allow input X-02-29 (leap day)
seasons = [('winter', (date(Y,  1,  1),  date(Y,  3, 20))),
           ('spring', (date(Y,  3, 21),  date(Y,  6, 20))),
           ('summer', (date(Y,  6, 21),  date(Y,  9, 22))),
           ('autumn', (date(Y,  9, 23),  date(Y, 12, 20))),
           ('winter', (date(Y, 12, 21),  date(Y, 12, 31)))]

def get_season(now):
    if isinstance(now, datetime):
        now = now.date()
    now = now.replace(year=Y)
    return next(season for season, (start, end) in seasons
                if start <= now <= end)



if (__name__ == "__main__"):
    alerts()