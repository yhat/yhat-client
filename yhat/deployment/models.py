import inspect
import json
import pickle
import sys
import os
import warnings
import random
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
    locally. It will give you the same results as you will see on a Yhat server.

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

class Variant(dict):
    """
    A Variant is an option to use in a SplitTestModel. Variants are composed of 3 properties:

        - label: string, this will be included in the model output to indicate which variant was run in the split test
        - method: string, this is a reference to the method that will be used when this variant is used
        - traffic_allocation: float, the percentage of traffic that will be routed to this variant for the split test

    >>> variants = [
    ...    Variant("A", "execute_a", 0.5),
    ...    Variant("B", "execute_b", 0.5),
    ... ]
    >>> variants = [
    ...    Variant("A", "execute_a", 0.5),
    ...    Variant("B", "execute_b", 0.3),
    ...    Variant("C", "execute_c", 0.2),
    ... ]
    >>> variants = [
    ...    Variant("SVM", "execute_svc", 0.7),
    ...    Variant("Logistic", "execute_logit", 0.3)
    ... ]
    """
    def __init__(self, label=None, method=None, traffic_allocation=0.5):
        self['label'] = label
        self['method'] = method
        self['traffic_allocation'] = traffic_allocation


class SplitTestModel(YhatModel):
    """
    Create an A/B testable model. This will split traffic between different
    models (specified as methods in your class).

    Examples
    ========

    class YetAnotherModel(SplitTestModel):
        variants = [
            Variant(label="SVC", method="execute_svc", traffic_allocation=0.5),
            Variant(label="LOGIT", method="execute_logit", traffic_allocation=0.5)
        ]

    class MyModel(SplitTestModel):
        variants = [
            Variant("A", "execute_a", 0.5),
            Variant("B", "execute_b", 0.4),
            Variant("C", "execute_c", 0.1)
        ]

    class AnotherModel(SplitTestModel):
        variants = [
            Variant("SVC", "execute_svc", 0.5),
            Variant("LOGIT", "execute_logit", 0.4),
            Variant("DEFAULT", "execute_default", 0.1)
        ]
    """

    def __init__(self, variants=None):
        if variants is None:
            variants = self.variants

        if sum(v['traffic_allocation'] for v in variants) != 1:
            msg = " + ".join([str(v['traffic_allocation']) for v in variants])
            msg += " = " + str(sum(v['traffic_allocation'] for v in variants))
            raise Exception("Your total traffic allocation for all variants must sum to 1!\n\t%s" % msg)

        for variant in variants:
            try:
                getattr(self, variant['method'])
            except:
                raise Exception("Method '{}' for variant '{}' does not exist".format(variant['method'], variant['label']))

        self.variants = variants
        super(SplitTestModel, self).__init__()


    def execute(self, data):
        r = random.random()
        total = 0.0
        for variant in self.variants:
            total += variant['traffic_allocation']
            if r < total:
                method = getattr(self, variant['method'])
                output = method(data)
                output['variant'] = variant['label']
                return output

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
