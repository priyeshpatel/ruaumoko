from __future__ import print_function

import os
import os.path
import sys
import re
import tempfile
import shutil
import zipfile

try:
    # Python3
    from urllib.request import urlopen, urlretrieve
    from urllib.parse import urlparse
except ImportError:
    # Python2
    from urllib import urlopen, urlretrieve
    from urlparse import urlparse


from . import dataset


class Downloader:
    def __init__(self, config):
        for attribute in ['url', 'regex', 'filename']:
            setattr(self, attribute, config['dataset'][attribute])

    def run(self):
        if os.path.exists(self.filename):
            print("Dataset already exists", file=sys.stderr)
            sys.exit(1)

        ds = dataset.DatasetWriter(self.filename)
        packs = sorted(self._retrieve_file_list())

        hgt_count = 0

        for count, pack in enumerate(packs):
            pack_path = urlparse(pack).path
            pack_name = os.path.basename(pack_path)

            with tempfile.TemporaryFile() as f:
                u = urlopen(pack)
                try:
                    shutil.copyfileobj(u, f)
                finally:
                    u.close()
                f.seek(0, 2)

                with zipfile.ZipFile(f, 'r') as pack:
                    for fn in pack.namelist():
                        loc = self._parse_filename(fn)
                        if loc:
                            cts = pack.read(fn)
                            ds.add_square(loc, cts)
                            hgt_count += 1
                        elif not fn.endswith('/'):
                            print("Warning: ignoring", pack_name, fn, file=sys.stderr)

            print("(%i/%i; %i) downloaded and extracted"
                    % (count, len(packs), hgt_count))

    def _retrieve_file_list(self):
        page = urlopen(self.url).read().decode('ascii')
        urls = set(re.findall(self.regex, page))
        return urls

    FN_REGEX = re.compile(r"(N|S)([0-9]{2})(W|E)([0-9]{3})\.hgt")

    def _parse_filename(self, filename):
        filename = os.path.basename(filename)
        match = self.FN_REGEX.match(filename)
        if match:
            ns, lat, we, lng = match.groups()
            lat = int(lat)
            if ns == 'S':
                lat *= -1
            lng = int(lng)
            if we == 'W':
                lng = 360 - lng
            if not (-90 <= lat <= 90) or not (0 <= lng < 360):
                raise ValueError("Bad cell location: %s, %s" % (lat, lng))
            return lat, lng
        else:
            return None
