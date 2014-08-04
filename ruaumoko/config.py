from os.path import join, dirname

import yaml

def load_config(file_name):
    with open(file_name) as f:
        config = yaml.safe_load(f)

    return config

def default_config():
    file_name = join(dirname(__file__), "default_config.yaml")
    return load_config(file_name)
