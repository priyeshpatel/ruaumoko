import os
from flask import Flask, abort, jsonify

from elevation import Elevation, NoDataError

app = Flask(__name__)
elevation = Elevation(os.environ['ELEVATION_CONFIG_YAML'])

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
