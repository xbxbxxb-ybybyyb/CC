import json

def read_json(path):
    with open(path, 'r') as fin:
        try:
            data = json.load(fin)
        except json.JSONDecodeError:
            data = None
    return data


def dump_json(path, value):
    with open(path, 'w') as fout:
        json.dump(value, fout, sort_keys=True, indent=4)


if __name__ == '__main__':
    # demo
    scaler = {'fct_001': {'scaler': {'type': 'ZSCORE',
                                     'param': {'mean': 0.0,
                                               'std':  1.0}}},
              'fct_002': {'scaler': {'type': 'ZSCORE',
                                     'param': {'mean': 1.0,
                                               'std':  2.0}}},
              'fct_003': {'scaler': {'type': 'MAXMIN',
                                     'param': {'max': 1.0,
                                               'min': 0.0}}},
             }
    dump_json('scaler.json', scaler)


