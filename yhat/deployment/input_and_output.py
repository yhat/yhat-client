import warnings
import json

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

def df_to_json(df):
    """
    Convert Pandas DataFrame to Yhat compatable json

    Parameters
    ----------
    df: Pandas DataFrame

    Returns
    -------
    json string: str
    """
    try:
        pd
    except NameError:
        raise ImportError("df_to_json() requires pandas")
    if not isinstance(df,pd.DataFrame):
        raise ValueError("'df' parameter must be a pandas DataFrame")
    if df.index.name:
        msg = "index values are NOT maintained through jsonifification," + \
                " consider resetting index";
        warnings.warn(msg)
    df_values = df.transpose().to_json(orient='values',date_format='iso')
    df_values = json.loads(df_values)
    try:
        from collections import OrderedDict
        df_values = OrderedDict(list(zip(df.columns,df_values)))
    except ImportError:
        df_values = dict(list(zip(df.columns,df_values)))
    return json.dumps(df_values)
