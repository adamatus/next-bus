#!/usr/bin/env python
import logging
import math
import sys
import time

import click
import requests

DEFAULT_HOST='http://svc.metrotransit.org'
ROUTE_PATH='/NexTrip/Routes'
DIR_PATH='/NexTrip/Directions/{route}'
STOP_PATH='/NexTrip/Stops/{route}/{direction}'
TIME_PATH='/NexTrip/{route}/{direction}/{stop}'

logging.basicConfig(format='%(message)s')

@click.command()
@click.argument('route')
@click.argument('stop')
@click.argument('direction')
@click.option('--date-time', '-d')
@click.option('--host', '-h', default=DEFAULT_HOST)
def next_bus(route, stop, direction, date_time, host):
    route_details = lookup_route(route, host + ROUTE_PATH)

    if route_details is None:
        sys.exit(1)

    direction_details = lookup_direction(direction, route_details, host + DIR_PATH)

    if direction_details is None:
        sys.exit(1)

    stop_details = lookup_stop(stop, route_details, direction_details, host + STOP_PATH)

    if stop_details is None:
        sys.exit(1)

    next_time = lookup_next_time(date_time, route_details, direction_details, stop_details, host + TIME_PATH)

    if next_time is None:
        sys.exit(1)

    print(next_time)


def make_request(url, endpoint_name):
    r = requests.get(url,
                     headers={'Accept': 'application/json'})

    if r.status_code != 200:
        logging.error('ERROR: {} endpoint misbehaved'.format(endpoint_name))
        return None

    return r.json()


def fetch_first(resource, resource_url, match_pattern, match_field, **kwargs):
    result = make_request(resource_url.format(**kwargs), resource)
    if result is None:
        return result

    items = [item for item in result if match_pattern.lower() in item[match_field].lower()]

    if len(items) == 1:
        return items[0]

    if len(items) == 0:
        logging.error('ERROR: {} not found'.format(resource))
    else:
        logging.error("ERROR: More than one {0} found. Please refine {0}".format(resource))

    return None


def lookup_route(route_pattern, route_url):
    return fetch_first('Route', route_url, route_pattern, 'Description')


def lookup_direction(direction_pattern, route, dir_url):
    return fetch_first('Direction', dir_url, direction_pattern, 'Text',
            route=route['Route'])


def lookup_stop(stop_pattern, route, direction, stop_url):
    return fetch_first('Stop', stop_url, stop_pattern, 'Text',
            route=route['Route'],direction=direction['Value'])


def lookup_next_time(date_time, route, direction, stop, time_url):
    times = make_request(time_url.format(route=route['Route'],direction=direction['Value'],stop=stop['Value']), 'Time')
    if times is None:
        return times

    if len(times) == 0:
        logging.error('ERROR: No scheduled departures remain')
        return None

    if times[0]['Actual']:
        return times[0]['DepartureText']
    else:
        return compute_time_to_departure(times[0]['DepartureTime'], date_time)


def compute_time_to_departure(departure_time, date_time):
    departure_time_only = extract_date_time(departure_time)
    if date_time is None:
        date_time = str(int(time.time())*1000)
    return str(math.floor((int(departure_time_only)-int(date_time))/1000/60)) + ' Min'


def extract_date_time(departure_time):
    return departure_time.split('(')[1].split('-')[0]


if __name__ == '__main__':
    next_bus()
