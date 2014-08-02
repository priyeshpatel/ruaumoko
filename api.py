import os
from flask import Flask, abort, jsonify

from elevation import config, Elevation, NoDataError

app = Flask(__name__)

cfg_file = os.environ.get('ELEVATION_CONFIG_YAML')
if cfg_file:
    cfg = config.load_config(cfg_file)
else:
    cfg = config.default_config()

elevation = Elevation(cfg)

@app.route('/<latitude>,<longitude>')
def main(latitude, longitude):
    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except ValueError:
        abort(400)

    try:
        return jsonify(elevation.lookup(latitude, longitude))
    except NoDataError:
        return "No data", 404

if __name__ == '__main__':
    app.run(debug=True)
