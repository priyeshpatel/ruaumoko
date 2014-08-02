from __future__ import print_function

import os
import sys
import re
import zipfile

try:
    # Python3
    from urllib.request import urlopen, urlretrieve
except ImportError:
    # Python2
    from urllib import urlopen, urlretrieve

class Downloader:
    def __init__(self, config):
        for attribute in ['url', 'regex', 'folder']:
            setattr(self, attribute, config['dataset'][attribute])

    def run(self):
        if os.path.exists(self.folder):
            print "Output folder already exists!"
            sys.exit(1)
        os.makedirs(self.folder)

        self.download_packs()

    def download_packs(self):
        packs = self.retrieve_file_list()
        total = len(packs)
        count = 0
        for pack in packs:
            count += 1
            self._extract_pack(self._download_pack(pack))
            print("(%i/%i) \"%s\" downloaded and extracted"
                        % (count, total, pack),
                  file=sys.stderr)

    def retrieve_file_list(self):
        page = urlopen(self.url).read().decode('ascii')
        urls = set(re.findall(self.regex, page))
        return urls

    def _download_pack(self, url):
        filename = os.path.join(self.folder, url.split('/')[-1])
        urlretrieve(url, filename)
        return filename

    def _extract_pack(self, path, delete=True):
        pack = zipfile.ZipFile(path, 'r')

        for hgt in pack.namelist():
            if not hgt.endswith("hgt"):
                continue

            filename = os.path.split(hgt)[1]
            first = True
            while filename in os.listdir(self.folder): 
                if first:
                    print("Duplicate HGT found: %s" % filename, file=sys.stderr)
                    first = False
                filename += ".copy"
            output_path = os.path.join(self.folder, filename)
            output = open(output_path, 'wb')
            output.write(pack.read(hgt))
            output.close()

        pack.close()

        if delete:
            os.remove(path)
