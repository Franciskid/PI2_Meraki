from influxdb_client import InfluxDBClient

from config import org, token, bucket, influx_url
from datetime import datetime, timedelta

import numpy

client = InfluxDBClient(url=influx_url, token=token, org=org)
query_api = client.query_api()

def get_average_temp(date):
    return get_average_temp_hum(date, 'temperature')

def get_average_hum(date):
    return get_average_temp_hum(date, 'humidity')


def get_average_temp_hum(date, metric):
    values = get_latest_reading(date, metric)

    #for key, value in values.items():
        #print(key, ' : ', value)

    data = list(values.values())

    mean = numpy.mean(data, axis=0)
    sd = numpy.std(data, axis=0)

    minTemp = mean - 0.5 * sd
    maxTemp = mean + 0.5 * sd
    final_data = [x for x in data if ((x > minTemp) & (x < maxTemp))]

    final_mean = numpy.mean(final_data)

    return final_mean

def format_date(td):
    return f'{td.days}d{td.seconds//3600}h{(td.seconds//60)%60}m{td.seconds % 60}s'


def get_latest_reading(date, metric):
    start = datetime.today() - date
    stop = (datetime.today() + timedelta(hours=1)) - date
    tables = query_api.query(f'from(bucket:"{bucket}")'
                             f' |> range(start: -{format_date(start)},'
                             f' stop:{format_date(stop)})'
                             f' |> filter(fn: (r) => r["_field"] == "{metric}")'
                             f' |> filter(fn: (r) => r["location"] == "L404")'
                             f' |> yield(name: "mean")')

    values = {}
    for table in tables:
        for record in table.records:
            if (record.get_measurement() not in values):
                values[record.get_measurement()] = record.get_value()

    return values


if (__name__ == "__main__"):
    print(get_average_temp(datetime.today() + timedelta(hours=-10)))
