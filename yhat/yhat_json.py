import json
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
    def __init__(self, nan_str="null", **kwargs):
        super(NumpyAwareJSONEncoder, self).__init__(**kwargs)
        self.nan_str = nan_str
        self.allow_nan = True

    def default(self, obj):
        if np and isinstance(obj, np.ndarray) and obj.ndim == 1:
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

    # uses code from official python json.encoder module. Same licence applies.
    def iterencode(self, o, _one_shot=False):
        """
        Encode the given object and yield each string representation as
        available.

        For example:
            for chunk in JSONEncoder().iterencode(bigobject):
                mysocket.write(chunk)
        """
        if self.check_circular:
            markers = {}
        else:
            markers = None
        if self.ensure_ascii:
            _encoder = json.encoder.encode_basestring_ascii

        else:
            _encoder = json.encoder.encode_basestring
        # if self.encoding != 'utf-8':
        #     def _encoder(o, _orig_encoder=_encoder, _encoding=self.encoding):
        #         if isinstance(o, str):
        #             o = o.decode(_encoding)
        #         return _orig_encoder(o)

        def floatstr(o, allow_nan=self.allow_nan, _repr=repr,
            _inf=json.encoder.INFINITY, _neginf=-json.encoder.INFINITY,
            nan_str=self.nan_str):
            # Check for specials.  Note that this type of test is processor
            # and/or platform-specific, so do tests which don't depend on the
            # internals.

            if o != o:
                text = nan_str
            elif o == _inf:
                text = 'Infinity'
            elif o == _neginf:
                text = '-Infinity'
            else:
                return _repr(o)

            if not allow_nan:
                raise ValueError(
                    "Out of range float values are not JSON compliant: " +
                    repr(o))

            return text

        _iterencode = json.encoder._make_iterencode(
                markers, self.default, _encoder, self.indent, floatstr,
                self.key_separator, self.item_separator, self.sort_keys,
                self.skipkeys, _one_shot)
        return _iterencode(o, 0)


# we're going to create a json de-serializer that will by default use
# NumpyAwareJSONEncoder with json
def json_dumps(data, **kwargs):
    """
    Uses json.dumps to serialize data into JSON. In addition to the standard
    json.dumps function, we're also using the NumpyAwareJSONEncoder to handle
    numpy arrays and the `ignore_nan` parameter by default to handle np.nan values.
    """
    return json.dumps(data, cls=NumpyAwareJSONEncoder, allow_nan=False)
