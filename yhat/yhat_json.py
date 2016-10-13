import simplejson as json
try:
    import numpy as np
except Exception as e:
    np = None

class NumpyAwareJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if np and isinstance(obj, np.ndarray) and obj.ndim == 1:
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


def _dumps(data):
    return __dumps(data, cls=NumpyAwareJSONEncoder, ignore_nan=True)

__dumps = json.dumps
json.dumps = _dumps
