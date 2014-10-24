"""Command-line utility to run/manage webapp."""
import os

from flask.ext.script import Manager
from .api import app

manager = Manager(app)

def main():
    if 'RUAUMOKO_SETTINGS' in os.environ:
        app.config.from_envvar('RUAUMOKO_SETTINGS')
    manager.run()
