# Mock data for test suite

This directory contains some mock data for testing ruaumoko without actually
having to download ~7GiB of data.

Use the ``generate-dem-chunks.sh`` script to convert a directory of
full-resolution DEM GeoTIFF tiles into a set of down-sampled tiles. The
down-sampled tiles are individually zip-ed and then collated into a single
super-zip. This rather curious arrangement is meant to match the way they are
stored on the download server.

The full-resolution chunks may be downloaded using the ruaumoko downloader
itself. See the ``--save-chunks`` option.
