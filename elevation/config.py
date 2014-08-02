import yaml

def load_config(file_name):
    with open(file_name) as f:
        config = yaml.safe_load(f)

    return config
