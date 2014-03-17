import os
import sys
import re
import urllib
import zipfile

from config import *

def retrieve_file_list():
    page = urllib.urlopen(DATASET_URL).read()
    urls = set(re.findall(DATASET_REGEX, page))
    return urls

def _download_pack(url):
    filename = os.path.join(DATASET_FOLDER, url.split('/')[-1])
    urllib.urlretrieve(url, filename)
    return filename

def _extract_pack(path, delete=True):
    pack = zipfile.ZipFile(path, 'r')

    for hgt in pack.namelist():
        if not hgt.endswith("hgt"):
            continue

        filename = os.path.split(hgt)[1]
        first = True
        while filename in os.listdir(DATASET_FOLDER): 
            if first:
                print "Duplicate HGT found: %s" % filename
                first = False
            filename += ".copy"
        output_path = os.path.join(DATASET_FOLDER, filename)
        output = open(output_path, 'wb')
        output.write(pack.read(hgt))
        output.close()

    pack.close()

    if delete:
        os.remove(path)

def download_packs():
    packs = retrieve_file_list()
    total = len(packs)
    count = 0
    for pack in packs:
        count += 1
        _extract_pack(_download_pack(pack))
        print "(%i/%i) \"%s\" downloaded and extracted" % (count, total, pack)

def main():
    if os.path.exists(DATASET_FOLDER):
        print "Output folder already exists!"
        sys.exit(1)
    os.makedirs(DATASET_FOLDER)

    download_packs()

if __name__ == "__main__":
    main()
