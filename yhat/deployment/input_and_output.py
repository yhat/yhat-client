import warnings
import json
from schema import Schema

try:
    import pandas as pd
except:
    warnings.warn("Could not import pandas")

def _make_df(data):
    """
    Takes an arbitrary data structure and tries to convert it into a data frame

    Parameters
    ----------
    data: object
        data to be converted into data frame

    Returns
    -------
    data: data frame
    """
    try:
        data = pd.DataFrame(data)
    except:
        data = pd.DataFrame([data])
    return data


def validate(schema):
    def real_decorator(function):
        def wrapper(*args, **kwargs):
            if isinstance(schema, Schema):
                schema.validate(args[1])
            else:
                warnings.warn("`schema` parameter passed to `@validate` is not a Schema object. Cannot validate schema.")

            return function(*args, **kwargs)
        return wrapper
    return real_decorator


def preprocess(func=None, **options):
    """
    Decorator for defining the following:
        1) data type for incoming data
        2) data type for returned data
        3) how to handle null values

    Parameters
    ----------
    in_type: (optional), dictionary or data frame
        indicates what the input data type should be
    out_type: (optional), dictionary or data frame
        indicates what the returned data type should be

    Returns
    -------
    partial/inner: function
        a function
    """
    if func != None:
        # We received the function on this call, so we can define
        # and return the inner function
        def inner(*args, **kwargs):        
            in_type = options.get('in_type', pd.DataFrame)
            out_type = options.get('out_type', pd.DataFrame)
            data = args[1]
            if in_type==pd.DataFrame:
                data = _make_df(data)
            data = func(args[0], data)
            if out_type==pd.DataFrame:
                data = _make_df(data)
            return data
        inner.__wrapped_func__ = func
   
        return inner
  
    else:
        # We didn't receive the function on this call, so the return value
        # of this call will receive it, and we're getting the options now.
        def partial_inner(func):
            return preprocess(func, **options)   
        return partial_inner

