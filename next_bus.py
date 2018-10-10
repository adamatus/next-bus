#!/usr/bin/env python
import logging
import math
import sys
import time

import click
import requests

DEFAULT_HOST='http://svc.metrotransit.org'
ROUTE_PATH='/NexTrip/Routes'
DIR_PATH='/NexTrip/Directions'
STOP_PATH='/NexTrip/Stops'
TIME_PATH='/NexTrip'

logging.basicConfig(format='%(message)s')

def lookup_route(route_pattern, route_url):
    r = requests.get(route_url,
                     headers={'Accept': 'application/json'})

    if r.status_code != 200:
        logging.error('ERROR: Route endpoint misbehaved')
        return None

    routes = [route for route in r.json() if route_pattern in route['Description']]

    if len(routes) == 1:
        return routes[0]

    if len(routes) == 0:
        logging.error('ERROR: Route not found')
    else:
        logging.error("ERROR: More than one route found. Please refine route")

    return None


def lookup_direction(direction_pattern, route, dir_url):
    r = requests.get(dir_url + "/" + route['Route'],
                     headers={'Accept': 'application/json'})

    if r.status_code != 200:
        logging.error('ERROR: Direction endpoint misbehaved')
        return None

    dirs = [direction for direction in r.json() if direction_pattern.lower() in direction['Text'].lower()]

    if len(dirs) == 1:
        return dirs[0]

    if len(dirs) == 0:
        logging.error('ERROR: Direction not found')
    else:
        logging.error("ERROR: More than one direction matched. Please refine direction")

    return None


def lookup_stop(stop_pattern, route, direction, stop_url):
    r = requests.get(stop_url + "/" + route['Route'] + "/" + direction['Value'],
                     headers={'Accept': 'application/json'})

    if r.status_code != 200:
        logging.error('ERROR: Stop endpoint misbehaved')
        return None

    stops = [stop for stop in r.json() if stop_pattern in stop['Text']]

    if len(stops) == 1:
        return stops[0]

    if len(stops) == 0:
        logging.error('ERROR: Stop not found')
    else:
        logging.error("ERROR: More than one stop matched. Please refine stop")

    return None

def lookup_next_time(date_time, route, direction, stop, time_url):
    r = requests.get(time_url + "/" + route['Route'] + "/" + direction['Value'] + "/" + stop['Value'],
                     headers={'Accept': 'application/json'})

    if r.status_code != 200:
        logging.error('ERROR: Time endpoint misbehaved')
        return None

    times = r.json()

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


if __name__ == '__main__':
    next_bus()
