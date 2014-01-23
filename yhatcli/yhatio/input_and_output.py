import warnings
import json

try:
    import pandas as pd
except:
    warnings.warn("Could not import pandas")

def make_df(data):
    if isinstance(data, pd.DataFrame):
        return data
    elif isinstance(data, dict):
        key = data.keys()[0]
        if isinstance(data[key], list):
            pass
        else:
            data = {k: [v] for k,v in data.items()}
    data = pd.DataFrame(data)
    return data


def parse_json(somejson):
    try:
        return json.loads(somejson)
    except Exception, e:
        print "Input was not valid JSON."
        print "==> %s" % str(e)

class df_to_df(object):
    """
    Decorator that coreces input and outputs into data frames.
    """
    def __init__(self, func):
        self.func = func
    
    def __call__(self, *args):
        data = args[0]
        data = make_df(data)
        result = self.func(self, data)
        return make_df(result)

class df_to_dict(object):
    """
    Decorator that coreces input to a data frame and requires the output to be
    a dictionary.
    """
    def __init__(self, func):
        self.func = func
    
    def __call__(self, *args):
        data = args[0]
        data = make_df(data)
        result = self.func(self, data)
        if isinstance(result, dict):
            return result
        else:
            msg = "Dictionary was not returned. '%s' was returned instead"
            msg = msg % str(type(result))
            raise Exception(msg)


class dict_to_dict(object):
    """
    Decorator that needs inputs and outputs to be dictionaries.
    """
    def __init__(self, func):
        self.func = func
    
    def __call__(self, *args):
        data = args[0]
        if isinstance(result, dict)==False:
            msg = "Dictionary was not given. '%s' was input instead"
            msg = msg % str(type(result))
            raise Exception(msg)
        result = self.func(self, data)
        if isinstance(result, dict):
            return result
        else:
            msg = "Dictionary was not returned. '%s' was returned instead"
            msg = msg % str(type(result))
            raise Exception(msg)


def handle_nulls(features, data):
    data = make_df(data)
    for feature in features:
        name = feature["name"]
        strategy = feature["na_filler"]
        if hasattr(strategy, '__call__')==False:
            strategy_func = lambda x: strategy
        else:
            strategy_func = strategy
        data[name] = data.apply(strategy_func, axis=1)
    return data


import pandas as pd

def make_df(data):
    if isinstance(data, dict):
        key = data.keys()[0]
        if isinstance(data[key], list):
            pass
        else:
            data = {k: [v] for k,v in data.items()}
    data = pd.DataFrame(data)
    return data

def handle_nulls(features, data):
    data = make_df(data)
    for feature in features:
        name = feature["name"]
        strategy = feature["na_filler"]
        if hasattr(strategy, '__call__')==False:
            strategy_func = lambda x: strategy
        else:
            strategy_func = strategy
        if name not in data:
            data[name] = None
        mask = data[name].isnull()
        data[name][mask] = data[mask].apply(strategy_func, axis=1)
    return data


def preprocess(func=None, **options):
    if func != None:
        # We received the function on this call, so we can define
        # and return the inner function
        def inner(*args, **kwargs):        
            in_type = options.get('in_type', pd.DataFrame)
            out_type = options.get('out_type', pd.DataFrame)
            null_handler = options.get('null_handler', None)
            data = args[1]
            if in_type==pd.DataFrame:
                data = make_df(data)
            if null_handler:
                data = handle_nulls(null_handler, data)
            data = func(args[0], data)
            if out_type==pd.DataFrame:
                data = make_df(data)
            return data
   
        return inner
  
    else:
        # We didn't receive the function on this call, so the return value
        # of this call will receive it, and we're getting the options now.
        def partial_inner(func):
            return preprocess(func, **options)   
        return partial_inner

