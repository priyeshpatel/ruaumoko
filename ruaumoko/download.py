# Copyright 2014 (C) Daniel Richman
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
"""
Download Digital Elevation Map (DEM) data for the Ruaumoko server.

Usage:
    ruaumoko-download (-h | --help)
    ruaumoko-download [(-v | --verbose)] [--host HOSTNAME] [--path PATH]
        [--tiff-file-pattern PATTERN] [--zip-file-pattern PATTERN]
        [<dataset-location>]

Options:
    -h, --help                      Print a brief usage summary.
    -v, --verbose                   Be verbose in logging progress.

    <dataset-location>              Location to store DEM dataset.
                                    [default: {default_location}]

Advanced options:
    --host HOSTNAME                 Host name of DEM server.
                                    [default: www.viewfinderpanoramas.org]
    --path PATH                     Path to DEM TIF files on server.
                                    [default: DEM/TIF15]
    --zip-file-pattern PATTERN      Pattern for zip file to fetch from server.
                                    [default: 15-<CHUNK>.zip]
    --tiff-file-pattern PATTERN     Pattern for TIFF file within zip file.
                                    [default: 15-<CHUNK>.tif]

    Filename patterns will have <CHUNK> replaced with the current chunk.

"""

from __future__ import print_function

import logging
import os
import shutil
import sys
import tempfile
import zipfile

from docopt import docopt
from sh import wget, convert, unzip
from six import iteritems
from six.moves.urllib.parse import urlunsplit

from . import Dataset
from ._compat import TemporaryDirectory

# HACK: interpolate dataset default location into docopt string.
__doc__ = __doc__.format(
    default_location = Dataset.default_location,
)

# Logger for the main utility
LOG = logging.getLogger(os.path.basename(sys.argv[0]))

EXPECT_SIZE = 14401 * 10801 * 2

def char_range(frm, to):
    # inclusive endpoints
    return map(chr, range(ord(frm), ord(to) + 1))

CHUNKS = list(char_range('A', 'X'))

def expand_pattern(pattern, **kwargs):
    """Interpolate filename patterns."""
    for k, v in kwargs.items():
        pattern = pattern.replace('<'+k+'>', v)
    return pattern

def download(target, temp_dir, host, path, zip_pattern, tiff_pattern):
    zip_path = os.path.join(temp_dir, "temp.zip")
    tgt_path = os.path.join(temp_dir, "chunk")

    for chunk_idx, chunk in enumerate(CHUNKS):
        LOG.info('Fetching chunk {0}/{1}'.format(chunk_idx+1, len(CHUNKS)))

        tif_name = expand_pattern(tiff_pattern, CHUNK=chunk)
        tif_path = os.path.join(temp_dir, tif_name)

        url = urlunsplit((
            'http', host, '/'.join((path, expand_pattern(zip_pattern, CHUNK=chunk))), '', ''
        ))
        LOG.info('GET-ing {0}'.format(url))
        wget(url, q=True, O=zip_path)
        
        with zipfile.ZipFile(zip_path, 'r') as pack:
            contents = pack.namelist()
            if contents != [tif_name]:
                raise ValueError("Bad archive contents: {:r}".format(contents))
        
        unzip(zip_path, d=temp_dir)
        os.unlink(zip_path)

        convert(tif_path, '-quiet', 'GRAY:{}'.format(tgt_path))
        os.unlink(tif_path)

        if os.stat(tgt_path).st_size != EXPECT_SIZE:
            raise ValueError("Bad converted size: {}".format(chunk))

        with open(tgt_path, "rb") as f:
            shutil.copyfileobj(f, target)
        os.unlink(tgt_path)

def main():
    opts = docopt(__doc__)
    logging.basicConfig(
        level=logging.INFO if opts['--verbose'] else logging.WARN,
        format='%(name)s:%(levelname)s: %(message)s'
    )

    target = opts['<dataset-location>'] or Dataset.default_location
    LOG.info('Downloading DEM to "{0}"'.format(target))

    with open(target, "wb") as target_f:
        with TemporaryDirectory() as temp_dir:
            download(
                target_f, temp_dir,
                host = opts['--host'], path = opts['--path'],
                tiff_pattern = opts['--tiff-file-pattern'],
                zip_pattern = opts['--zip-file-pattern'],
            )

if __name__ == "__main__":
    main()
