import json
import yaml

def load_yaml(filename):
    return yaml.load(open(filename))

def load_json(filename):
        try:
                data = json.load(open(filename))
        except:
                return None

        return data

def pretty_dump(data):
        return json.dumps(data, indent=4, separators=(',', ': '),ensure_ascii=False).encode('utf8')