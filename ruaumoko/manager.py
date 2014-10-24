"""Command-line utility to run/manage webapp."""

from flask.ext.script import Manager
from .api import app

manager = Manager(app)

def main():
    manager.run()
