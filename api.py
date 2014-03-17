from flask import Flask, abort, jsonify
import math
import os
import struct

from config import *
from elevation import *

app = Flask(__name__)

@app.route('/<latitude>,<longitude>')
def main(latitude, longitude):
    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except ValueError:
        abort(400)

    try:
        return jsonify(elevation(latitude, longitude))
    except NoDataError:
        return "No data", 404

if __name__ == '__main__':
    app.run(debug=True)
