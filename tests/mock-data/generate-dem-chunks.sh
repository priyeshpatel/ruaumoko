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
tile_width=20
tile_height=10

show_usage() {
    cat >&2 <<EOI
Generate a downsampled set of DEM data from a directory containing DEM GeoTIFFs.

Usage:
    $0 [-h?] [-w WIDTH] [-e HEIGHT] [--] <zip-output> <dataset-output>
        <dem-directory>
EOI
}

show_full_usage() {
    show_usage
    cat >&2 <<EOI

Options:
    -h, -?              Show a brief usage summary.

    -w WIDTH            Resample DEMs to WIDTH wide. [default: $tile_width]
    -e HEIGHT           Resample DEMs to HEIGHT high. [default: $tile_height]

    <zip-output>        Zip file to write downsampled DEM tiles to.
    <dataset-output>    File to write raw data to.
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
        w)
            tile_width=${OPTARG}
            ;;
        e)
            tile_height=${OPTARG}
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

# Do we have the right number of positional options?
if [ "$#" != 3 ]; then
    show_usage
    exit 1
fi

# Extract positional options.
zip_file=$1
dataset_file=$2
dem_directory=$3

# Create temporary directory which is deleted on script exit.
tmp_dir=`mktemp -dt dem-chunk.XXXXXX`
cleanup_tmp() {
    rm -fr "$tmp_dir"
}
trap cleanup_tmp EXIT

# Delete output file if it exists
if [ -f "$dataset_file" ]; then
    rm "$dataset_file"
fi

# Process DEM tiles.
for tile_fn in "$dem_directory/"*; do
    echo "Processing ${tile_fn}..."
    tiff_output_fn="$tmp_dir/`basename $tile_fn`"
    zip_output_fn="$tmp_dir/`basename $tile_fn .tif`.zip"
    raw_output_fn="$tmp_dir/raw"
    echo "    ... downsampling"
    gdalwarp -r average -ts "$tile_width" "$tile_height" "$tile_fn" "$tiff_output_fn"
    echo "    ... extracting"
    convert -quiet "$tiff_output_fn" "GRAY:$raw_output_fn"
    cat "$raw_output_fn" >>"$dataset_file"
    echo "    ... compressing"
    zip -9 "$zip_output_fn" -j "$tmp_dir" "$tmp_dir/`basename $tile_fn`"

    rm "$tiff_output_fn" "$raw_output_fn"
done

# Compress (deleting file if it already exists)
if [ -f "$zip_file" ]; then
    rm "$zip_file"
fi
zip -9 "$zip_file" -j "$tmp_dir" "$tmp_dir/"*

# Cleanup
cleanup_tmp
