import subprocess

import pytest
from grappa_http import should
from pretenders.client.http import HTTPMock
from pretenders.common.constants import FOREVER

from next_bus import ROUTE_PATH, DIR_PATH, STOP_PATH, TIME_PATH

SCRIPT_NAME='./next_bus.py'

def setup_routes_happy_path(live_mock):
    live_mock.when('GET ' + ROUTE_PATH).reply("""[
      {
        "Description": "METRO Blue Line",
        "ProviderID": "8",
        "Route": "901"
      },
      {
        "Description": "METRO Green Line",
        "ProviderID": "8",
        "Route": "902"
      },
      {
        "Description": "5 - Brklyn Center - Fremont - 26th Av - Chicago - MOA",
        "ProviderID": "8",
        "Route": "5"
      }
    ]""", headers={'Content-Type': 'application/json'}, status=200)


def setup_directions_happy_path(live_mock, route):
    live_mock.when('GET ' + DIR_PATH.format(route=route)).reply("""[
      {
        "Text": "NORTHBOUND",
        "Value": "4"
      },
      {
        "Text": "SOUTHBOUND",
        "Value": "1"
      }
    ]""", headers={'Content-Type': 'application/json'}, status=200)


def setup_stops_happy_path(live_mock, route, direction):
    live_mock.when('GET ' + STOP_PATH.format(route=route,direction=direction)).reply("""[
      {
        "Text": "44th Ave  and Fremont Ave ",
        "Value": "44FM"
      },
      {
        "Text": "Osseo Rd and 47th Ave ",
        "Value": "47OS"
      },
      {
        "Text": "Brooklyn Center Transit Center",
        "Value": "BCTC"
      }
    ]""", headers={'Content-Type': 'application/json'}, status=200)

def setup_times_actual_true_happy_path(live_mock, route, direction, stop):
    live_mock.when('GET ' + TIME_PATH.format(route=route,direction=direction,stop=stop)).reply("""[
      {
        "Actual": true,
        "BlockNumber": 1078,
        "DepartureText": "16 Min",
        "DepartureTime": "\\/Date(1538971260000-0500)\\/",
        "Description": "Fremont Av\\/Brklyn Ctr\\/Transit Ctr",
        "Gate": "",
        "Route": "5",
        "RouteDirection": "SOUTHBOUND",
        "Terminal": "M",
        "VehicleHeading": 0,
        "VehicleLatitude": 44.95512,
        "VehicleLongitude": -93.26259
      },
      {
        "Actual": false,
        "BlockNumber": 1220,
        "DepartureText": "11:44",
        "DepartureTime": "\\/Date(1538973840000-0500)\\/",
        "Description": "Fremont Av\\/Brklyn Ctr\\/Transit Ctr",
        "Gate": "",
        "Route": "5",
        "RouteDirection": "SOUTHBOUND",
        "Terminal": "M",
        "VehicleHeading": 0,
        "VehicleLatitude": 44.85284,
        "VehicleLongitude": -93.23808
      }
    ]""", headers={'Content-Type': 'application/json'}, status=200)

def setup_times_actual_false_happy_path(live_mock, route, direction, stop):
    live_mock.when('GET ' + TIME_PATH.format(route=route,direction=direction,stop=stop)).reply("""[
      {
        "Actual": false,
        "BlockNumber": 1078,
        "DepartureText": "11:01",
        "DepartureTime": "\\/Date(1538971260000-0500)\\/",
        "Description": "Fremont Av\\/Brklyn Ctr\\/Transit Ctr",
        "Gate": "",
        "Route": "5",
        "RouteDirection": "SOUTHBOUND",
        "Terminal": "M",
        "VehicleHeading": 0,
        "VehicleLatitude": 44.95512,
        "VehicleLongitude": -93.26259
      },
      {
        "Actual": false,
        "BlockNumber": 1220,
        "DepartureText": "11:44",
        "DepartureTime": "\\/Date(1538973840000-0500)\\/",
        "Description": "Fremont Av\\/Brklyn Ctr\\/Transit Ctr",
        "Gate": "",
        "Route": "5",
        "RouteDirection": "SOUTHBOUND",
        "Terminal": "M",
        "VehicleHeading": 0,
        "VehicleLatitude": 44.85284,
        "VehicleLongitude": -93.23808
      }
    ]""", headers={'Content-Type': 'application/json'}, status=200)


mock = HTTPMock('localhost', 55555)

@pytest.fixture
def cli_runner():
    def runner(command, *arguments):
        p = subprocess.Popen([command] + list(arguments),
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        return dict(returncode=p.returncode,
                    stdout=stdout.decode('ASCII'),
                    stderr=stderr.decode('ASCII'))
    return runner



def test_help(cli_runner):
    result = cli_runner(SCRIPT_NAME, '--help')

    result | should.have.key('returncode').that.should.equal(0)
    result | should.have.key('stdout')
    result['stdout'] | should.startswith('Usage: next_bus.py [OPTIONS] ROUTE STOP DIRECTION')
    result['stdout'] | should.contain('-d, --date-time TEXT')
    result['stdout'] | should.contain('-h, --host TEXT')

def test_route_endpoint_returns_non_200(cli_runner):
    mock.reset()
    mock.when('GET ' + ROUTE_PATH).reply(status=404, times=FOREVER)

    result = cli_runner(SCRIPT_NAME, '-d 20181007234100-05:00', '-h ' + mock.pretend_url,
                        '5 - Brooklyn Center', 'Brooklyn Center', 'south')

    result | should.have.key('returncode').that.should.equal(1)
    result | should.have.key('stderr')
    result['stderr'] | should.equal('ERROR: Route endpoint misbehaved\n')

def test_bad_route(cli_runner):
    mock.reset()
    setup_routes_happy_path(mock)

    result = cli_runner(SCRIPT_NAME, '-d 20181007234100-05:00', '-h ' + mock.pretend_url,
                        '5 - Brooklyn Center', 'Brooklyn Center', 'south')

    result | should.have.key('returncode').that.should.equal(1)
    result | should.have.key('stderr')
    result['stderr'] | should.equal('ERROR: Route not found\n')

def test_bad_direction(cli_runner):
    mock.reset()
    setup_routes_happy_path(mock)
    setup_directions_happy_path(mock, '5')

    result = cli_runner(SCRIPT_NAME, '-d 20181007234100-05:00', '-h ' + mock.pretend_url,
                        '5 - Brklyn Center', 'Brooklyn Center', 'west')

    result | should.have.key('returncode').that.should.equal(1)
    result | should.have.key('stderr')
    result['stderr'] | should.equal('ERROR: Direction not found\n')

def test_direction_endpoint_returns_non_200(cli_runner):
    mock.reset()
    setup_routes_happy_path(mock)
    mock.when('GET ' + DIR_PATH.format(route='5')).reply(status=404, times=FOREVER)

    result = cli_runner(SCRIPT_NAME, '-d 20181007234100-05:00', '-h ' + mock.pretend_url,
                        '5 - Brklyn Center', 'Brooklyn Center', 'south')

    result | should.have.key('returncode').that.should.equal(1)
    result | should.have.key('stderr')
    result['stderr'] | should.equal('ERROR: Direction endpoint misbehaved\n')

def test_multiple_directions(cli_runner):
    mock.reset()
    setup_routes_happy_path(mock)
    setup_directions_happy_path(mock, '5')

    result = cli_runner(SCRIPT_NAME, '-d 20181007234100-05:00', '-h ' + mock.pretend_url,
                        '5 - Brklyn Center', 'Brooklyn Center', 'bound')

    result | should.have.key('returncode').that.should.equal(1)
    result | should.have.key('stderr')
    result['stderr'] | should.equal('ERROR: More than one Direction found. Please refine Direction\n')

def test_stop_endpoint_returns_non_200(cli_runner):
    mock.reset()
    setup_routes_happy_path(mock)
    setup_directions_happy_path(mock, '5')
    mock.when('GET ' + STOP_PATH.format(route=5,direction=1)).reply(status=404, times=FOREVER)

    result = cli_runner(SCRIPT_NAME, '-d 20181007234100-05:00', '-h ' + mock.pretend_url,
                        '5 - Brklyn Center', 'Brooklyn Center', 'south')

    result | should.have.key('returncode').that.should.equal(1)
    result | should.have.key('stderr')
    result['stderr'] | should.equal('ERROR: Stop endpoint misbehaved\n')

def test_bad_stop(cli_runner):
    mock.reset()
    setup_routes_happy_path(mock)
    setup_directions_happy_path(mock, '5')
    setup_stops_happy_path(mock, '5', '1')

    result = cli_runner(SCRIPT_NAME, '-d 20181007234100-05:00', '-h ' + mock.pretend_url,
                        '5 - Brklyn Center', 'NON-EXISTANT', 'south')

    result | should.have.key('returncode').that.should.equal(1)
    result | should.have.key('stderr')
    result['stderr'] | should.equal('ERROR: Stop not found\n')

def test_times_endpoint_returns_non_200(cli_runner):
    mock.reset()
    setup_routes_happy_path(mock)
    setup_directions_happy_path(mock, '5')
    setup_stops_happy_path(mock, '5', '1')
    mock.when('GET ' + TIME_PATH.format(route='5',direction='1',stop="7SOL")).reply(status=404, times=FOREVER)

    result = cli_runner(SCRIPT_NAME, '-d 20181007234100-05:00', '-h ' + mock.pretend_url,
                        '5 - Brklyn Center', 'Brooklyn Center', 'south')

    result | should.have.key('returncode').that.should.equal(1)
    result | should.have.key('stderr')
    result['stderr'] | should.equal('ERROR: Time endpoint misbehaved\n')

def test_successful_lookup(cli_runner):
    mock.reset()
    setup_routes_happy_path(mock)
    setup_directions_happy_path(mock, '5')
    setup_stops_happy_path(mock, '5', '1')
    setup_times_actual_true_happy_path(mock, '5', '1', 'BCTC')

    result = cli_runner(SCRIPT_NAME, '-d 20181007234100-05:00', '-h ' + mock.pretend_url,
                        '5 - Brklyn Center', 'Brooklyn Center', 'south')

    print(result['stderr'])

    result | should.have.key('returncode').that.should.equal(0)
    result | should.have.key('stdout')
    result['stdout'] | should.equal('16 Min\n')

def test_successful_lookup_later_stop(cli_runner):
    mock.reset()
    setup_routes_happy_path(mock)
    setup_directions_happy_path(mock, '5')
    setup_stops_happy_path(mock, '5', '1')
    setup_times_actual_false_happy_path(mock, '5', '1', '44FM')

    result = cli_runner(SCRIPT_NAME, '-d 1538969940000', '-h ' + mock.pretend_url,
                        '5 - Brklyn Center', '44th', 'south')

    print(result['stderr'])

    result | should.have.key('returncode').that.should.equal(0)
    result | should.have.key('stdout')
    result['stdout'] | should.equal('22 Min\n')

# TODO Error on direction that doesn't make sense based on stop?
