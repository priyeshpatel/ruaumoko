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

from __future__ import print_function

import sys
import os
import shutil
import tempfile
import zipfile

from os import path

from sh import wget, convert, unzip

from . import Dataset

URL_FORMAT = "http://www.viewfinderpanoramas.org/DEM/TIF15/15-{}.zip"
TIF_FORMAT = "15-{}.tif"
EXPECT_SIZE = 14401 * 10801 * 2

def char_range(frm, to):
    # inclusive endpoints
    return map(chr, range(ord(frm), ord(to) + 1))

CHUNKS = list(char_range('A', 'X'))

def download(target, temp_dir):
    zip_path = path.join(temp_dir, "temp.zip")
    tgt_path = path.join(temp_dir, "chunk")

    for chunk in CHUNKS:
        tif_name = TIF_FORMAT.format(chunk)
        tif_path = path.join(temp_dir, tif_name)

        wget(URL_FORMAT.format(chunk), q=True, O=zip_path)
        
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
    if len(sys.argv) == 1:
        target = Dataset.default_location
    elif len(sys.argv) == 2:
        target = sys.argv[1]
    else:
        print("Usage: {} [{}]".format(sys.argv[0], Dataset.default_location))
        sys.exit(1)

    with open(target, "wb") as target_f:
        with tempfile.TemporaryDirectory() as temp_dir:
            download(target_f, temp_dir)

if __name__ == "__main__":
    main()
