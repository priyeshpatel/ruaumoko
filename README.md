# Ruaumoko: Elevation API for Tawhiri

A Python module and web API for worldwide elevation data.

This project is a part of the larger [Tawhiri Landing Predictor
Software](https://github.com/cuspaceflight/tawhiri).

The digital elevation data is sourced from the [Viewfinder
Panoramas](http://www.viewfinderpanoramas.org/dem3.html) website.

See the CUSF wiki for more details: http://www.cusf.co.uk/wiki/ruaumoko.

## Authors

See AUTHORS.

## License

Ruaumoko is Copyright 2014 (see AUTHORS & individual files) and licensed under
the [GNU GPL 3](http://gplv3.fsf.org/) (see LICENSE).

## Dataset Format

Throughout Ruaumoko, data is indexed latitude-first/row-first

The 15-arcsecond (i.e., dividing a degree into 240 points) data comes as a
grid of 24 TIFs, named A-X (C layout).
Each TIF is a 10801 by 14401 array of 16 bit signed integers.
The download script concatenates the arrays (after unpacking the TIFs) to get
a single binary file, which is cast to an array with dimensions
`(4, 6, 10801, 14401)`.

Note that `4 * 10800 = 180 * 240` and `6 * 14400 = 360 * 240`.

Each TIF overlaps with the ones on each side by one row, that is, the 10801th
row of 'A' is the same as the 1st row of chunk 'G'.

The top left corner of chunk A is at (lat) 90 (lng) -180. Latitude decreases
down the rows; longitude increases along the columns.
