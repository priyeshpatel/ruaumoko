"""
Generate an ASCII art image of elevation from a dataset.

Usage:
    {me} (-h | --help)
    {me} [--shape WxH] [--tile-shape WxH] [<dataset>]

Options:
    -h, --help                  Show a brief usage summary.

    -s WxH, --shape WxH         Generate output W characters wide and H
                                characters high. [default: {def_shape[0]}x{def_shape[1]}]

    --tile-shape WxH            Expected shape of tiles is W pixels wide and H
                                pixels high. [default: {def_tile_shape[0]}x{def_tile_shape[1]}]

    <dataset>                   Ruaumoko dataset to load elevation from.
                                [default: {def_ds_loc}]
"""
import logging
import math
import os
import sys
import traceback

import docopt

from ruaumoko import Dataset

# HACK: Update doc-string with defaults
__doc__ = __doc__.format(
    me = os.path.basename(sys.argv[0]),
    def_shape = (78,25),
    def_tile_shape = Dataset.default_res,
    def_ds_loc = Dataset.default_location,
)

LOG = logging.getLogger(os.path.basename(sys.argv[0]))

def parse_shape(shape_str, name='shape'):
    try:
        shape = tuple(int(x) for x in shape_str.split('x'))
    except ValueError as e:
        LOG.error('Invalid {1}: {0}'.format(shape_str, name))
        raise e

    if len(shape) != 2 or any(x<=0 for x in shape):
        LOG.error('Two non-zero and positive integers required for {0}.'.format(name))
        raise ValueError('Invalid shape')

    return shape

def main():
    logging.basicConfig(level=logging.WARN)
    opts = docopt.docopt(__doc__)

    try:
        shape = parse_shape(opts['--shape'])
        tile_res = parse_shape(opts['--tile-shape'])
    except ValueError:
        return 1

    # Open dataset
    ds_loc = opts['<dataset>'] or Dataset.default_location
    ds = Dataset(ds_loc, expected_res=tile_res)

    # Generate elevation image
    elev_img = []
    max_elev = 0.0
    for row in range(shape[1]):
        elev_row = []
        lat = - ((float(row) / shape[1]) * 178 - 89)
        for col in range(shape[0]):
            lng = (180 + (float(col) / shape[0]) * 359 + 1) % 360
            elev = math.sqrt(max(0, ds.get(lat, lng)))
            max_elev = max(elev, max_elev)
            elev_row.append(elev)
        elev_img.append(elev_row)

    # Format elevation image as ASCII art
    dots = ' .:-=+*#%@'
    for er in elev_img:
        sys.stdout.write(
            ''.join(dots[max(0, min(len(dots)-1, int((len(dots)*e)/max_elev)))] for e in er)
        )
        sys.stdout.write('\n')

    return 0 # success

if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as e:
        LOG.error('Unrecoverable error: {0}'.format(traceback.format_exc()))
        sys.exit(1)
