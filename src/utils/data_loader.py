import json

def load_test_data(path):
    with open(path) as f:
        return json.load(f)