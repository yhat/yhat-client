import pickle
import requests
import json
import urllib
import pprint as pp
import inspect
import re

class Model(object):
    def __init__(self, **kwargs):
        for kw, arg in kwargs.iteritems():
            if kw=="requirements":
                arg = open(arg).read().strip()
            setattr(self, kw, arg)

class BaseModel(Model):
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
        return rawData

    def predict(self, transformedData):
        """
        Predict executes your predictive model, formats the data into response,
        and returns it.
        """
        return self.clf.predict(transformedData)
    
    def execute(self, data):
        self.require()
        data = self.transform(data)
        return self.predict(data)

class StepModel(Model):
    """
    StepModel allows you to define steps as methods. Each step is numbered
    (i.e. step_1, step_2, step_3, etc.). Steps are executed in order with the 
    output from the previous step becoming the input to the next step.
    ====================================================================
    Example:

    class MyModel(StepModel):
        def step_1(self, data):
            return 1
        def step_2(self, data):
            return [data, 2]
        def step_3(self, data):
            return data + [3]
    mm = MyModel()
    print mm.execute(None)
    # [1, 2, 3]
    # This executes like so...
    # one = mm.step_1(None)
    # two = mm.step_2(one)
    # three = mm.step_3(two)
    # print three
    """
    def _get_steps(self):
        steps = []
        for name, step in inspect.getmembers(self, predicate=inspect.ismethod):
            if re.match("step_", name):
                order = name.lstrip("step_")
                try:
                    order = int(order)
                except:
                    raise Exception("'%s' - step names must be integers" % name)
                steps.append((order, name, step))
        steps = sorted(steps, key=lambda x: x[0])
        return steps
    
    def execute(self, data):
        for _, name, step in self._get_steps():
            try:
                data = step(data)
            except Exception, e:
                print "Error executing step: '%s'" % name
                print "Exception: %s" % str(e)
                return
        return data

