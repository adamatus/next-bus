# Next Bus Clock

This CLI utility will help you determine how long you'll have to wait for the next
available MetroTransit ride on the route, stop, and direction of your choice!

# Installation

This utility relies on Python 3.+ (but might work under 2.6+).  Given the highly
experimental and top-secret nature of this project, it has not been packaged
for distribution.  In order to run it you must manually install the required
python dependencies (preferably in a virtualenv):

    pip install -r requirements.txt

# Usage

Example:

    ./next_bus.py "5 - Brklyn Center" "Brooklyn Center" "south"
    8 Min

For detailed help:

    ./next_bus.py --help

# Development

## Install dev dependencies

    pip install -r dev-requirements

## Start fake services

In a console, run:

    python -m pretenders.server.server --host 0.0.0.0 --port 55555 

## Run tests

In a different console, run:

    pytest .
