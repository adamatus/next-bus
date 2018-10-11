import pook
import pytest
import time
import unittest

from grappa import should

from next_bus import *

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


class TestLookupRoute(unittest.TestCase):

    @pook.on
    def setUp(self):
        self.route_url = FAKE_HOST+ROUTE_PATH
        self.mock = pook.get(self.route_url, reply=200, response_json=ROUTES)

    def test_lookup_route_returns_None_if_not_200_response(self):
        self.mock = pook.get(self.route_url, reply=404)
        route = lookup_route('ignored', self.route_url)
        route | should.be.none

    def test_lookup_route_returns_empty_list_if_not_found_in_response(self):
        route = lookup_route('junk', self.route_url)
        route | should.be.none

    def test_lookup_route_returns_None_if_more_than_one_found(self):
        route = lookup_route('METRO', self.route_url)
        route | should.be.none

    def test_lookup_route_returns_match(self):
        route = lookup_route('Brklyn Center', self.route_url)
        route | should.have.key("Description")
        route | should.have.key("ProviderID")


class TestLookupDirection(unittest.TestCase):

    @pook.on
    def setUp(self):
        self.dir_url = FAKE_HOST+DIR_PATH
        self.mock = pook.get(self.dir_url.format(route=ROUTES[2]['Route']), reply=200, response_json=DIRS)

    def test_lookup_direction_returns_None_if_not_200_response(self):
        self.mock = pook.get(self.dir_url.format(route=ROUTES[2]['Route']), reply=404)
        route = lookup_direction('ignored', ROUTES[2], self.dir_url)
        route | should.be.none

    def test_lookup_direction_returns_empty_list_if_not_found_in_response(self):
        route = lookup_direction('junk', ROUTES[2], self.dir_url)
        route | should.be.none

    def test_lookup_direction_returns_None_if_more_than_one_found(self):
        route = lookup_direction('BOUND', ROUTES[2], self.dir_url)
        route | should.be.none

    def test_lookup_direction_returns_match(self):
        route = lookup_direction('SOUTHBOUND', ROUTES[2], self.dir_url)
        route | should.have.key("Value").that.should.equal("1")

    def test_lookup_direction_returns_caseinsensitive_match(self):
        self.mock = pook.get(self.dir_url.format(route=ROUTES[1]['Route']), reply=200, response_json=DIRS)
        route = lookup_direction('north', ROUTES[1], self.dir_url)
        route | should.have.key("Value").that.should.equal("4")


class TestLookupStop(unittest.TestCase):

    @pook.on
    def setUp(self):
        self.stop_url_template = FAKE_HOST+DIR_PATH
        self.stop_url=self.stop_url_template.format(route=ROUTES[2]['Route'],direction=DIRS[1]['Value'])
        self.mock = pook.get(self.stop_url, reply=200, response_json=STOPS)

    def test_lookup_stop_returns_None_if_not_200_response(self):
        self.mock = pook.get(self.stop_url, reply=404)
        route = lookup_stop('ignored', ROUTES[2], DIRS[1], self.stop_url_template)
        route | should.be.none

    def test_lookup_stop_returns_empty_list_if_not_found_in_response(self):
        route = lookup_stop('junk', ROUTES[2], DIRS[1], self.stop_url_template)
        route | should.be.none

    def test_lookup_stop_returns_None_if_more_than_one_found(self):
        route = lookup_stop('Ave', ROUTES[2], DIRS[1], self.stop_url_template)
        route | should.be.none

    def test_lookup_stop_returns_match(self):
        route = lookup_stop('Brooklyn Center', ROUTES[2], DIRS[1], self.stop_url_template)
        route | should.have.key("Value").that.should.equal("BCTC")


class TestLookupTime(unittest.TestCase):

    @pook.on
    def setUp(self):
        self.time_url_template = FAKE_HOST+TIME_PATH
        self.time_url=self.time_url_template.format(route=ROUTES[2]['Route'],direction=DIRS[1]['Value'],stop=STOPS[2]['Value'])

    def test_lookup_time_returns_None_if_not_200_response(self):
        mock = pook.get(self.time_url, reply=404)
        next_time = lookup_next_time('ignored', ROUTES[2], DIRS[1], STOPS[2], self.time_url_template)
        next_time | should.be.none

    def test_lookup_time_returns_None_if_no_times(self):
        mock = pook.get(self.time_url, reply=200, response_json="[]")
        next_time = lookup_next_time('ignored', ROUTES[2], DIRS[1], STOPS[2], self.time_url_template)
        next_time | should.be.none

    def test_lookup_time_returns_first_match(self):
        mock = pook.get(self.time_url, reply=200, response_json=TIMES_ACTUAL)
        next_time = lookup_next_time('ignored', ROUTES[2], DIRS[1], STOPS[2], self.time_url_template)
        next_time | should.equal("16 Min")

    def test_lookup_time_converts_non_actual_times(self):
        mock = pook.get(self.time_url, reply=200, response_json=TIMES_NONACTUAL)
        next_time = lookup_next_time('1538969940000', ROUTES[2], DIRS[1], STOPS[2], self.time_url_template)
        next_time | should.equal("22 Min")


# Simple helper method tests below

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
