import inspect
import json
import pickle
import sys
import os
import warnings
import re
from pip.operations import freeze

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
    REQUIREMENTS = []
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

    def add_requirement(self, package_name=None, package_version=None, req_file=None, pip_freeze=False, conda_file=None, git_uri=None):
        """
        explicily add a package requirment to the model

        Parameters
        ----------
        package_name: name of the required package on conda or pip ex: scikit-learn
        package_version: (optional) to be used with package_name ex: 0.17.1
            or
        req_file: text file of requirements in the form:
                <package_name>==<package_version>
                scikit-image==0.12.3
                scikit-learn==0.17.1
                scipy==0.17.0
            or
        pip_freeze: set to True to use your pip freeze as the list of requirements
            or
        conda_file: use this, run `conda list --export > package-list.txt` and pass in this
                file path as the conda_file
            or
        git_uri: URI to [public] Git project like these:
            #  https://git.myproject.org/MyProject#egg=MyProject
        """
        # If there are more than 20 packages, show a warning
        PACKAGE_WARNING = 20
        pkgList = []
        pkgCount = 0
        if package_name != None:
            if package_version != None:
                pkgCount += 1
                pkgList.append(package_name + "==" + package_version)
            else:
                pkgCount += 1
                pkgList.append(package_name)

        elif req_file != None:
            f = open(req_file, 'r')
            for line in f:
                if line[0] != '#':
                    pkgCount += 1
                    pkgList.append(line)
            f.close()

        elif pip_freeze:
            x = freeze.freeze()
            for p in x:
                pkgCount += 1
                pkgList.append(p)

        elif conda_file != None:
            f = open(conda_file, 'r')
            pkgCount = 0
            for line in f:
                if line[0] != '#':
                    pkgCount += 1
                    splitLine = line.split('=')
                    pkgList.append(splitLine[0] + '==' + splitLine[1])

            f.close()

        elif git_uri != None:
            if git_uri[:4] == 'http':
                pkgCount += 1
                pkgList.append('git+' + git_uri)
            # elif git_uri[:4] == 'git@':
            #     self.REQUIREMENTS.append(git_uri)
            # elif git_uri[:6] == 'ssh://':
            #     self.REQUIREMENTS.append(git_uri)
            # elif git_uri[:6] == 'git://':
            #     self.REQUIREMENTS.append(git_uri)
            else:
                print git_uri + " is an unrecognized git resource. \
                Please use HTTPS"
        else:
            print "you haven't specified a requirement!"

        if pkgCount > PACKAGE_WARNING:
            warnings.warn(
                "\nYou are reqiring %s packages. \n"
                "Please consider explicily adding fewer requirements to avoid build issues. \n"
                "These packages will not be added...\n" % str(pkgCount)
            )
        else:
            self.REQUIREMENTS.extend(pkgList)

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
