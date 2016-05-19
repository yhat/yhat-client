import inspect
import json
import pickle
import sys
import os
import warnings
import re

from input_and_output import df_to_df, parse_json, preprocess

try:
    import pandas as pd
except:
    warnings.warn("Could not import pandas")


class YhatModel(object):
    """
    A simple class structure for your model. Place all of the code you want to
    execute in the `execute` method.

    The `run` method provides you with a basic development "server" for testing
    locally. It will give you the same results as you will see on a Yhat server
    99% of the time.

    Parameters
    ----------
    filename: string
        filename of saved model
    """
    def __init__(self, filename=None):
        if filename is not None:
            pickles = json.load(open(filename, 'rb'))
            for varname, pickled_value in pickles.get('objects', {}).items():
                globals()[varname] = pickle.loads(pickled_value)

    @preprocess
    def execute(self, data):
        """
        This is the execution plan for your model. It defines what routines you
        will execute and how the input and output will be handled.

        Parameters
        ----------
        data: dict or DataFrame
            the datatype is decided by the IO Specification; (df_to_df,
            dict_to_dict, etc.).
        """
        pass

class Model(object):
    def __init__(self, **kwargs):
        for kw, arg in kwargs.iteritems():
            if kw=="requirements":
                arg = open(arg).read().strip()
            setattr(self, kw, arg)

class BaseModel(Model):
    __name__ = "BaseModel"
    """
    BaseModel is the standard Yhat model class that gives your model
    the functionality to run it as a RESTful API. Once you create your own
    model, you need to implement the following functions:
         - transform
         - predict
    """
    def require(self):
        """
        Define what libraries and modules you want to include in your project
        ====================================================================
        def require(self):
            from StringIO import StringIO
            from string import letters
        """
        pass

    def transform(self, rawData):
        """
        Transform takes the raw data that's going to be sent to your yhat API
        and converts it into the format required to be run through your model.
        """
        pass

    def predict(self, transformedData):
        """
        Predict executes your predictive model, formats the data into response,
        and returns it.
        """
        pass

    def execute(self, data):
        self.require()
        data = self.transform(data)
        return self.predict(data)
