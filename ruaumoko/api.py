# Copyright 2014 (C) Priyesh Patel, Daniel Richman
#
# This file is part of Ruaumoko.
# https://github.com/cuspaceflight/ruaumoko
#
# Ruaumoko is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ruaumoko is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ruaumoko. If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function

import sys
from flask import Flask, abort, jsonify

from . import Dataset

app = Flask(__name__)


@app.before_first_request
def open_dataset():
    global elevation

    dir = app.config.get('ELEVATION_DIRECTORY', Dataset.default_location)
    elevation = Dataset(dir)


@app.route('/<latitude>,<longitude>')
def get_elevation(latitude, longitude):
    try:
        latitude = float(latitude)
        longitude = float(longitude)
        result = elevation.get(latitude, longitude)
    except ValueError:
        abort(400)

    return jsonify({"elevation": result})


def main():
    if sys.argv[1:] == ["--debug"]:
        app.run(debug=True)
    elif sys.argv[1:] == []:
        app.run()
    else:
        print("Usage: {} [--debug]".format(sys.argv[0]), file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
