import simplejson as json
# we're not going to require numpy as a hard requirement as it can be a huge
# pain to install. *most* of our customers will already have it installed. the ones
# that don't are most likely just doing a lightweight test (i.e. HelloWorld) and
# installing numpy would just be really annoying.
try:
    import numpy as np
except ImportError as e:
    np = None

class NumpyAwareJSONEncoder(json.JSONEncoder):
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
        return json.JSONEncoder.default(self, obj)

# this is patching simplejson's dumps method so that it will use our NumpyAwareJSONEncoder
# by default AND it will also handle np.nan values as well--it will serialize them
# as `null`.
#
# first we save the original simplejson.dumps as original_dumps so we can use it
# in yhat_dumps. next we create a function called yhat_dumps that we'll wrap
# around original_dumps(simplejson.dumps) and have it default to use our json
# encoder and the ignore_nan parameter. last we assign yhat_dumps to json.dumps
# so it'll be used by default when you do `from yhat import json` (this will be
# in the kernel)

original_dumps = json.dumps

def yhat_dumps(data):
    """
    Uses simplejson.dumps to serialize data into JSON. In addition to the standard
    simplejson.dumps function, we're also using the NumpyAwareJSONEncoder to handle
    numpy arrays and the `ignore_nan` parameter by default to handle np.nan values.
    """
    return original_dumps(data, cls=NumpyAwareJSONEncoder, ignore_nan=True)

json.dumps = yhat_dumps
