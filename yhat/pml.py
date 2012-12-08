import pickle
import requests
import json
import urllib
import pprint as pp
import inspect
        

class BaseModel(object):
    def __init__(self, **kwargs):
        for kw, arg in kwargs.iteritems():
            setattr(self, kw, arg)

    def transform(self, rawData):
        return rawData

    def predict(self, transformedData):
        return self.clf.predict(transformedData)