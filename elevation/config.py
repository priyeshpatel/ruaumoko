import os.path

import yaml

def load_config(file_name):
    with open(file_name) as f:
        config = yaml.safe_load(f)

    return config

def default_config():
    from os.path import *
    file_name = join(dirname(__file__), "default_config.yaml")
    return load_config(file_name)
