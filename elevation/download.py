import os
import sys
import re
import urllib
import zipfile

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
            print "(%i/%i) \"%s\" downloaded and extracted" % (count, total, pack)

    def retrieve_file_list(self):
        page = urllib.urlopen(self.url).read()
        urls = set(re.findall(self.regex, page))
        return urls

    def _download_pack(self, url):
        filename = os.path.join(self.folder, url.split('/')[-1])
        urllib.urlretrieve(url, filename)
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
                    print "Duplicate HGT found: %s" % filename
                    first = False
                filename += ".copy"
            output_path = os.path.join(self.folder, filename)
            output = open(output_path, 'wb')
            output.write(pack.read(hgt))
            output.close()

        pack.close()

        if delete:
            os.remove(path)
