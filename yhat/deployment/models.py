import inspect
import json
import pickle
import sys
import os
import warnings
import re

from flask import Flask, request, render_template, jsonify

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

    def execution_plan(self, data):
        return self.execute(data)

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

    def serve(self, host='localhost', port=5000):
        """
        Creates a test server on port 5000 for testing purposes. This is a way to test
        your model before you deploy it to production.
        """
        template_folder = os.path.join(os.getcwd(), "templates")
        app = Flask(__name__, template_folder=template_folder)
        @app.route("/", methods=['GET', 'POST'])
        def testserver():
            if request.method=="GET":
                return render_template("demo.html")
            elif request.method=="POST":
                data = request.json
                try:
                    result = self.execute(data)
                    try:
                        import pandas as pd
                        if isinstance(result, pd.DataFrame):
                            result = result.transpose().to_json(orient='values',date_format='iso')
                            result = json.loads(result)
                    except ImportError:
                        None
                    return jsonify(result)
                except Exception, e:
                    result = {"error": str(e)}
                    return jsonify(result)
            else:
                return "Not Implemented."
        app.run(host=host, port=port, debug=True)

    def run(self, testcase=None):
        """
        Runs a local 'Yhat Server' that mimics the production environment. Data
        can be passed to the server via stdin (by pasting data into the terminal
        ).
        
        If your data is too big to paste into the terminal, try setting up a 
        testcase which will run automatically. To do this, use the json module
        and run json.dumps({ YOUR DATA}) to generate acceptable input for Yhat.

        Parameters
        ----------
        testcase: optional, JSON string
            If a testcase is included, it will automatically execute when `run`
            is called.
        """
        print "Paste your test data here"
        print "Data should be formatted as valid JSON."
        print "Hit <ENTER> to execute your model"
        print "Press <CTRL + C> or type 'quit' to exit"
        print "="*40
        if testcase:
            sys.stdout.write("[In] %s\n" % testcase)
            data = parse_json(testcase + '\n')
            sys.stdout.write("[Out]\n")
            print self.execute(data)
        while True:
            sys.stdout.write("[In] ")
            data = sys.stdin.readline()
            if data.strip()=="quit":
                sys.exit()
            data = parse_json(data)
            sys.stdout.write("[Out]\n")
            print self.execute(data)


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