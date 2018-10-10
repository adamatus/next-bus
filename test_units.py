import pook
import pytest
import time

from grappa import should

FAKE_HOST='http://fake.fake'
ROUTES=[
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
    ]

DIRS=[
      {
        "Text": "NORTHBOUND",
        "Value": "4"
      },
      {
        "Text": "SOUTHBOUND",
        "Value": "1"
      }
    ]

STOPS=[
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
    ]

TIMES_ACTUAL=[
      {
        "Actual": True,
        "BlockNumber": 1078,
        "DepartureText": "16 Min",
        "DepartureTime": "\\/Date(1538971260000-0500)\\/",
        "Description": "Fremont Av\\/Brklyn Ctr\\/Transit Ctr",
        "Gate": "",
        "Route": "5",
        "RouteDirection": "NORTHBOUND",
        "Terminal": "M",
        "VehicleHeading": 0,
        "VehicleLatitude": 44.95512,
        "VehicleLongitude": -93.26259
      },
      {
        "Actual": False,
        "BlockNumber": 1220,
        "DepartureText": "11:44",
        "DepartureTime": "\\/Date(1538973840000-0500)\\/",
        "Description": "Fremont Av\\/Brklyn Ctr\\/Transit Ctr",
        "Gate": "",
        "Route": "5",
        "RouteDirection": "NORTHBOUND",
        "Terminal": "M",
        "VehicleHeading": 0,
        "VehicleLatitude": 44.85284,
        "VehicleLongitude": -93.23808
      }
  ]

TIMES_NONACTUAL=[
      {
        "Actual": False,
        "BlockNumber": 1078,
        "DepartureText": "11:01",
        "DepartureTime": "\\/Date(1538971260000-0500)\\/",
        "Description": "Fremont Av\\/Brklyn Ctr\\/Transit Ctr",
        "Gate": "",
        "Route": "5",
        "RouteDirection": "NORTHBOUND",
        "Terminal": "M",
        "VehicleHeading": 0,
        "VehicleLatitude": 44.95512,
        "VehicleLongitude": -93.26259
      },
      {
        "Actual": False,
        "BlockNumber": 1220,
        "DepartureText": "11:44",
        "DepartureTime": "\\/Date(1538973840000-0500)\\/",
        "Description": "Fremont Av\\/Brklyn Ctr\\/Transit Ctr",
        "Gate": "",
        "Route": "5",
        "RouteDirection": "NORTHBOUND",
        "Terminal": "M",
        "VehicleHeading": 0,
        "VehicleLatitude": 44.85284,
        "VehicleLongitude": -93.23808
      }
  ]


@pytest.fixture
def route_response():
    return ROUTES

@pytest.fixture
def direction_response():
    return DIRS

@pytest.fixture
def stops_response():
    return STOPS

@pytest.fixture
def times_response():
    return TIMES_ACTUAL


from next_bus import ROUTE_PATH, lookup_route

ROUTE_URL=FAKE_HOST+ROUTE_PATH
@pook.on
def test_lookup_route_returns_empty_list_if_not_found_in_response(route_response):
    mock = pook.get(ROUTE_URL, reply=200, response_json=route_response)

    route = lookup_route('junk', ROUTE_URL)
    route | should.be.none

@pook.on
def test_lookup_route_returns_None_if_not_200_response():
    mock = pook.get(ROUTE_URL, reply=404)

    route = lookup_route('ignored', ROUTE_URL)
    route | should.be.none

@pook.on
def test_lookup_route_returns_None_if_more_than_one_found(route_response):
    mock = pook.get(ROUTE_URL, reply=200, response_json=route_response)

    route = lookup_route('METRO', ROUTE_URL)
    route | should.be.none
@pook.on
def test_lookup_route_returns_match(route_response):
    mock = pook.get(ROUTE_URL, reply=200, response_json=route_response)

    route = lookup_route('Brklyn Center', ROUTE_URL)
    route | should.have.key("Description")
    route | should.have.key("ProviderID")


from next_bus import DIR_PATH, lookup_direction

DIR_URL=FAKE_HOST+DIR_PATH

@pook.on
def test_lookup_direction_returns_empty_list_if_not_found_in_response(direction_response):
    mock = pook.get(DIR_URL+"/"+ROUTES[2]['Route'], reply=200, response_json=direction_response)

    route = lookup_direction('junk', ROUTES[2], DIR_URL)
    route | should.be.none

@pook.on
def test_lookup_direction_returns_None_if_not_200_response():
    mock = pook.get(DIR_URL+"/"+ROUTES[2]['Route'], reply=404)

    route = lookup_direction('ignored', ROUTES[2], DIR_URL)
    route | should.be.none

@pook.on
def test_lookup_direction_returns_None_if_more_than_one_found(direction_response):
    mock = pook.get(DIR_URL+"/"+ROUTES[2]['Route'], reply=200, response_json=direction_response)

    route = lookup_direction('BOUND', ROUTES[2], DIR_URL)
    route | should.be.none

@pook.on
def test_lookup_direction_returns_match(direction_response):
    mock = pook.get(DIR_URL+"/"+ROUTES[2]['Route'], reply=200, response_json=direction_response)

    route = lookup_direction('SOUTHBOUND', ROUTES[2], DIR_URL)
    route | should.have.key("Value").that.should.equal("1")

@pook.on
def test_lookup_direction_returns_caseinsensitive_match(direction_response):
    mock = pook.get(DIR_URL+"/"+ROUTES[1]['Route'], reply=200, response_json=direction_response)

    route = lookup_direction('north', ROUTES[1], DIR_URL)
    route | should.have.key("Value").that.should.equal("4")

from next_bus import STOP_PATH, lookup_stop

STOP_URL=FAKE_HOST+STOP_PATH

@pook.on
def test_lookup_stop_returns_empty_list_if_not_found_in_response(stops_response):
    mock = pook.get(STOP_URL+"/"+ROUTES[2]['Route']+"/"+DIRS[1]['Value'], reply=200, response_json=stops_response)

    route = lookup_stop('junk', ROUTES[2], DIRS[1], STOP_URL)
    route | should.be.none

@pook.on
def test_lookup_stop_returns_None_if_not_200_response():
    mock = pook.get(STOP_URL+"/"+ROUTES[2]['Route']+"/"+DIRS[1]['Value'], reply=404)

    route = lookup_stop('ignored', ROUTES[2], DIRS[1], STOP_URL)
    route | should.be.none

@pook.on
def test_lookup_stop_returns_None_if_more_than_one_found(stops_response):
    mock = pook.get(STOP_URL+"/"+ROUTES[2]['Route']+"/"+DIRS[1]['Value'], reply=200, response_json=stops_response)

    route = lookup_stop('Ave', ROUTES[2], DIRS[1], STOP_URL)
    route | should.be.none

@pook.on
def test_lookup_stop_returns_match(stops_response):
    mock = pook.get(STOP_URL+"/"+ROUTES[2]['Route']+"/"+DIRS[1]['Value'], reply=200, response_json=stops_response)

    route = lookup_stop('Brooklyn Center', ROUTES[2], DIRS[1], STOP_URL)
    route | should.have.key("Value").that.should.equal("BCTC")

from next_bus import TIME_PATH, lookup_next_time

TIME_URL=FAKE_HOST+TIME_PATH

@pook.on
def test_lookup_time_returns_None_if_not_200_response():
    mock = pook.get(TIME_URL+"/"+ROUTES[2]['Route']+"/"+DIRS[1]['Value']+"/"+STOPS[2]['Value'], reply=404)

    next_time = lookup_next_time('ignored', ROUTES[2], DIRS[1], STOPS[2], TIME_URL)
    next_time | should.be.none

@pook.on
def test_lookup_time_returns_None_if_no_times(times_response):
    mock = pook.get(TIME_URL+"/"+ROUTES[2]['Route']+"/"+DIRS[1]['Value']+"/"+STOPS[2]['Value'],
            reply=200, response_json="[]")

    next_time = lookup_next_time('ignored', ROUTES[2], DIRS[1], STOPS[2], TIME_URL)
    next_time | should.be.none

@pook.on
def test_lookup_time_returns_first_match(times_response):
    mock = pook.get(TIME_URL+"/"+ROUTES[2]['Route']+"/"+DIRS[1]['Value']+"/"+STOPS[2]['Value'],
            reply=200, response_json=TIMES_ACTUAL)

    next_time = lookup_next_time('ignored', ROUTES[2], DIRS[1], STOPS[2], TIME_URL)
    next_time | should.equal("16 Min")

@pook.on
def test_lookup_time_converts_non_actual_times(times_response):
    mock = pook.get(TIME_URL+"/"+ROUTES[2]['Route']+"/"+DIRS[1]['Value']+"/"+STOPS[2]['Value'],
            reply=200, response_json=TIMES_NONACTUAL)

    next_time = lookup_next_time('1538969940000', ROUTES[2], DIRS[1], STOPS[2], TIME_URL)
    next_time | should.equal("22 Min")

from next_bus import compute_time_to_departure, extract_date_time

def test_extract():
    extracted = extract_date_time("\\/Date(1538971260000-0500)\\/")

    extracted | should.equal("1538971260000")

def test_compute_time_to_depature_with_provided_datetime():
    next_time = compute_time_to_departure("\\/Date(1538971260000-0500)\\/", '1538969940000')

    next_time | should.equal("22 Min")

def test_compute_time_to_depature_without_provided_datetime():
    # This test could be flakey if we are right on the minute boundary
    # when getting time in setup...

    now = int(time.time()) * 1000
    then = now + (20 * 60 * 1000)

    next_time = compute_time_to_departure("\\/Date("+str(then)+"-0500)\\/", None)

    next_time | should.equal("20 Min")
