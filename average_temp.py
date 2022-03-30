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
    values = get_date_reading(date, metric)

    data = list(values.values())

    return get_average_from_data(data)


def format_date(td):
    return f'{td.days}d{td.seconds//3600}h{(td.seconds//60)%60}m{td.seconds % 60}s'


def get_date_reading(date, metric):
    stop = datetime.now() - date
    start = (datetime.now() + timedelta(hours=24)) - date
    tables = query_api.query(f'from(bucket:"{bucket}")'
                             f' |> range(start: -{format_date(start)}, stop:-{format_date(stop)})'
                             f' |> filter(fn: (r) => r["_field"] == "{metric}")'
                             f' |> filter(fn: (r) => r["location"] == "L404")'
                             f' |> yield(name: "last")')

    values = {}
    for table in tables:
        record = table.records[-1] #last metric
        if (record.get_measurement() not in values):
            values[record.get_measurement()] = record.get_value()

    return values
    
def get_range_mean_reading(date_beg, date_end = datetime.now(), metric = "temperature"):
    stop = datetime.now() - date_end
    start = datetime.now() - date_beg
    tables = query_api.query(f'from(bucket:"{bucket}")'
                             f' |> range(start: -{format_date(start)}, stop:-{format_date(stop)})'
                             f' |> filter(fn: (r) => r["_field"] == "{metric}")'
                             f' |> filter(fn: (r) => r["location"] == "L404")'
                             f' |> aggregateWindow(every:1h, fn:mean, createEmpty: true)'
                             f' |> yield(name: "mean")')

    values = {}
    amount_of_measurements = {}
    for table in tables:
        for record in table.records:
            if (record.get_measurement() not in values):
                values[record.get_measurement()] = record.get_value()
                amount_of_measurements[record.get_measurement()] = 1
            else:
                values[record.get_measurement()] += record.get_value()
                amount_of_measurements[record.get_measurement()] += 1

    values_mean = {k: v / amount_of_measurements[k] for k, v in values.items()}

    return get_average_from_data(list(values_mean.values()))


def get_average_from_data(values):
    mean = numpy.mean(values, axis=0)
    sd = numpy.std(values, axis=0)

    minTemp = mean - 0.5 * sd
    maxTemp = mean + 0.5 * sd
    final_data = [x for x in values if ((x > minTemp) & (x < maxTemp))]

    final_mean = numpy.mean(final_data)

    return final_mean


if (__name__ == "__main__"):
    #print(get_average_temp(datetime.now() - timedelta(hours=452)))
    print(get_range_mean_reading(datetime.now() - timedelta(days=2), datetime.now() - timedelta(days=1), "temperature"))
