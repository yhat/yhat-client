import pickle
import requests
import json
import urllib
import pprint as pp
import inspect
        

class BaseModel(object):
    """
    BaseModel is the standard Yhat model class that gives your model
    the functionality to run it as a RESTful API. Once you create your own
    model, you need to implement the following functions:
         - transform
         - predict
    """
    def __init__(self, **kwargs):
        for kw, arg in kwargs.iteritems():
            setattr(self, kw, arg)

    def require(self):
        """
        Define what libraries and modules you want to include in your project
        ====================================================================
        def require(self):
            from StringIO import StringIO
            from string import letters
        """
        pass

    def user_functions(self):
        """
        Define any functions you want to include in your project
        ====================================================================
        def hello_world():
            return "Hello World!"
        ...

        def user_functions(self):
            return ["hello_word"]
        """
        pass

    def transform(self, rawData):
        """
        Transform takes the raw data that's going to be sent to your yhat API and
        converts it into the format required to be run through your model.
        """
        return rawData

    def predict(self, transformedData):
        """
        Predict executes your predictive model, formats the data into response, and
        returns it.
        """
        return self.clf.predict(transformedData)