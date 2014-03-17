import math
import os
import struct

from config import *

class NoDataError(Exception):
    pass

def elevation(latitude, longitude):
    lat = math.floor(latitude)
    lon = math.floor(longitude)

    lat_prefix = "N" if lat >= 0 else "S"
    lon_prefix = "E" if lon >= 0 else "W"

    filename = FILENAME_FORMAT.format(lat_prefix, abs(lat), 
            lon_prefix, abs(lon))
    filename = os.path.join(DATASET_FOLDER, filename)

    if not os.path.isfile(filename):
        raise NoDataError()

    data = []
    with open(filename, 'rb') as f:
        data = struct.unpack(">1442401H", f.read())

    row = CELL_SIZE - int(round((latitude - lat) * CELL_SIZE))
    col = int(round((longitude - lon) * CELL_SIZE))

    result = {
            'latitude': latitude,
            'longitude': longitude, 
            'row' : row,
            'col' : col,
            'filename': filename,
            'elevation': data[row * (CELL_SIZE + 1) + col],
        }

    return result
