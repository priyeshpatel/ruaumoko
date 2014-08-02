import os
from flask import Flask, abort, jsonify, g

from elevation import config, Elevation, NoDataError

app = Flask(__name__)

@app.before_first_request
def load_config():
    cfg_file = app.config.get('ELEVATION_CONFIG_YAML')
    if cfg_file:
        cfg = config.load_config(cfg_file)
    else:
        cfg = config.default_config()

    g['elevation'] = Elevation(cfg)

@app.route('/<latitude>,<longitude>')
def main(latitude, longitude):
    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except ValueError:
        abort(400)

    try:
        return jsonify(g['elevation'].lookup(latitude, longitude))
    except NoDataError:
        return "No data", 404
