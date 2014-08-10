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

from . import Dataset

def main():
    if len(sys.argv) == 3:
        filename = Dataset.default_location
        _, latitude, longitude = sys.argv
    elif len(sys.argv) == 4:
        _, filename, latitude, longitude = sys.argv
    else:
        print("usage: {} [{}] LATITUDE LONGITUDE"
                .format(sys.argv[0], Dataset.default_location),
              file=sys.stderr)
        sys.exit(2)

    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except ValueError as e:
        print(e)
        sys.exit(2)

    elevation = Dataset(filename)
    print(elevation.get(latitude, longitude))

if __name__ == "__main__":
    main()
