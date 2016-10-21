import simplejson
# we're not going to require numpy as a hard requirement as it can be a huge
# pain to install. *most* of our customers will already have it installed. the ones
# that don't are most likely just doing a lightweight test (i.e. HelloWorld) and
# installing numpy would just be really annoying.
try:
    import numpy as np
except ImportError as e:
    np = None

class NumpyAwareJSONEncoder(simplejson.JSONEncoder):
    """
    NumpyAwareJSONEncoder makes numpy arrays JSON serializeable. This is important
    because most mathematical libraries return numpy arrays instead of python lists.

    If there was a new numpy data type that you wanted to make JSON serializeable,
    all you'd need to do is edit the `default` method below. This could also be
    modified in the future to serialize non-numpy specific data types (though you'd
    prboably want to change the name of the class).
    """
    def default(self, obj):
        if np and isinstance(obj, np.ndarray) and obj.ndim == 1:
            return obj.tolist()
        return simplejson.JSONEncoder.default(self, obj)


# we're going to create a json de-serializer that will by default use
# NumpyAwareJSONEncoder with simplejson
def json_dumps(data):
    """
    Uses simplejson.dumps to serialize data into JSON. In addition to the standard
    simplejson.dumps function, we're also using the NumpyAwareJSONEncoder to handle
    numpy arrays and the `ignore_nan` parameter by default to handle np.nan values.
    """
    return simplejson.dumps(data, cls=NumpyAwareJSONEncoder, ignore_nan=True)
