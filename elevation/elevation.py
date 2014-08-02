import math
import os
import struct

from .config import load_config

class NoDataError(Exception):
    pass

class Elevation():
    def __init__(self, config_file):
        config = load_config(config_file)

        for attribute in ['folder', 'filename_format', 'cell_size']:
            setattr(self, attribute, config['dataset'][attribute])

    def lookup(self, latitude, longitude):
        lat = math.floor(latitude)
        lon = math.floor(longitude)

        lat_prefix = "N" if lat >= 0 else "S"
        lon_prefix = "E" if lon >= 0 else "W"

        filename = self.filename_format.format(lat_prefix, abs(lat), 
                lon_prefix, abs(lon))
        filename = os.path.join(self.folder, filename)

        if not os.path.isfile(filename):
            raise NoDataError()

        data = []
        with open(filename, 'rb') as f:
            data = struct.unpack(">1442401H", f.read())

        row = (self.cell_size - 1) - int(round((latitude - lat) *
            (self.cell_size - 1)))
        col = int(round((longitude - lon) * (self.cell_size - 1)))

        result = {
                'latitude': latitude,
                'longitude': longitude, 
                'row' : row,
                'col' : col,
                'filename': filename,
                'elevation': data[row * self.cell_size + col],
            }

        return result
