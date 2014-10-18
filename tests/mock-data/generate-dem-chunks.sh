#!/bin/sh
#
# Requirements:
#   - zip
#   - GDAL
#
# Copyright 2014 (C) Rich Wareham <rich.cusf@richwareham.com>
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

# Defaults
tile_size=8

show_usage() {
    cat >&2 <<EOI
Generate a downsampled set of DEM data from a directory containing DEM GeoTIFFs.

Usage:
    $0 [-h?] [-t SIZE] [--] <zip-output> <dem-directory>
EOI
}

show_full_usage() {
    show_usage
    cat >&2 <<EOI

Options:
    -h, -?              Show a brief usage summary.

    -t SIZE             Resample DEMs to SIZE x SIZE tiles. [default: $tile_size]

    <zip-output>        Zip file to write downsampled DEM tiles to.
    <dem-directory>     Directory conaining DEM GeoTIFF tiles.

    Use "--" to separate positional options from switches.
EOI
}

while getopts "h?t:" opt; do
    case "$opt" in
        h|\?)
            show_full_usage
            exit 0
            ;;
        t)
            tile_size=${OPTARG}
            ;;
        *)
            echo "Unknown option: $opt" >&2
            show_usage
            exit 1
    esac
done

# Shift off command line options and (optional) [--] separator.
shift $((OPTIND-1))
[ "$1" = "--" ] && shift

# Do we have exactly two options?
if [ "$#" != 2 ]; then
    show_usage
    exit 1
fi

# Extract positional options.
zip_file=$1
dem_directory=$2

# Create temporary directory which is deleted on script exit.
tmp_dir=`mktemp -dt dem-chunk.XXXXXX`
cleanup_tmp() {
    rm -fr "$tmp_dir"
}
trap cleanup_tmp EXIT

# Process DEM tiles.
for tile_fn in "$dem_directory/"*; do
    echo "Processing ${tile_fn}..."
    gdalwarp -r average -ts "$tile_size" "$tile_size" "$tile_fn" "$tmp_dir/`basename $tile_fn`"
    zip -9 "$tmp_dir/`basename $tile_fn .tif`.zip" -j "$tmp_dir" "$tmp_dir/`basename $tile_fn`"
    rm "$tmp_dir/`basename $tile_fn`"
done

# Compress (deleting file if it already exists)
if [ -f "$zip_file" ]; then
    rm "$zip_file"
fi
zip -9 "$zip_file" -j "$tmp_dir" "$tmp_dir/"*

# Cleanup
cleanup_tmp
