import sys
import warnings
import base64
import json
import pickle
import terragon
import urllib2
import urllib
import types
import websocket
import uuid
import tempfile
import zlib
import re
import os
import os.path
import subprocess
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
from progressbar import ProgressBar, Percentage, Bar, FileTransferSpeed, ETA

from deployment.models import YhatModel
from deployment.save_session import save_function, _get_source
from .utils import progressbarify, sizeof_fmt

devnull = open(os.devnull, "w")

# If we can't import everything we need to detect requirements from
# this version of pip, then we just warn and turn off the feature.
try:
    from requirements import getExplicitRequirmets, getImplicitRequirements
except ImportError:
    warnings.warn("Unable to use this version of pip. Requirements detection disabled. Consider upgrading pip.")
    DETECT_REQUIREMENTS = False
else:
    DETECT_REQUIREMENTS = True


BASE_URI = "http://api.yhathq.com/"


class API(object):

    """
    An abstract class that implements some of the more generic methods for
    interacting with REST APIs.

    Parameters
    ----------
    base_uri: string
        URI of the API that you're working with
    """

    def __init__(self, base_uri):
        self.base_uri = base_uri
        self.headers = {'Content-Type': 'application/json'}

    def _get(self, endpoint, params):
        """
        Parameters
        ----------
        endpoint: string
            name of the rest endpoint you want to hit
        params: dictionary
            querystring parameters for API call

        Returns
        -------
        data: dictionary
            whatever is returned by the API
        """
        try:
            url = self.base_uri + endpoint + "?" + urllib.urlencode(params)
            req = urllib2.Request(url)
            req.add_header('Content-Type', 'application/json')
            auth = '%s:%s' % (params['username'], params['apikey'])
            base64string = base64.encodestring(auth).replace('\n', '')
            req.add_header("Authorization", "Basic %s" % base64string)
            response = urllib2.urlopen(req)
            rsp = response.read()
            return json.loads(rsp)
        except Exception, e:
            raise e

    def _post(self, endpoint, params, data, pb=False):
        """
        Parameters
        ----------
        endpoint: string
            name of the rest endpoint you want to hit
        params: dictionary
            querystring parameters for API call
        data: dictionary
            data you want transfered as JSON
        pb: bool
            do you want a progress bar?

        Returns
        -------
        data: dictionary
            whatever is returned by the API
        """
        try:
            url = self.base_uri + endpoint + "?" + urllib.urlencode(params)
            req = urllib2.Request(url)
            req.add_header('Content-Type', 'application/json')
            auth = '%s:%s' % (params['username'], params['apikey'])
            base64string = base64.encodestring(auth).replace('\n', '')
            req.add_header("Authorization", "Basic %s" % base64string)
            try:
                data = json.dumps(data)
            except Exception, e:
                msg = """Whoops. The data you're trying to send could not be
converted into JSON. If the data you're attempting to send includes a numpy
array, try casting it to a list (x.tolist()), or consider structuring your data
as a pandas DataFrame. If you're still having trouble, please contact:
{URL}.""".format(URL="support@yhathq.com")
                print msg
                return
            if pb:
                data = progressbarify(data)
            response = urllib2.urlopen(req, data)
            rsp = response.read()
            try:
                return json.loads(rsp)
            except ValueError:
                msg = """
        Could not unpack response values.
        Please visit "http://cloud.yhathq.com"
        to make sure your model is online and not still building."""
                raise Exception(msg)
        except Exception, e:
            raise e
            print "Message: %s" % str(rsp)

    def _post_file(self, endpoint, params, data, pb=True):
        # Register the streaming http handlers with urllib2
        register_openers()

        widgets = ['Transfering Model: ', Bar(), Percentage(), ' ', ETA(), ' ', FileTransferSpeed()]
        pbar = ProgressBar(widgets=widgets).start()
        def progress(param, current, total):
            if not param:
                return
            pbar.maxval = total
            pbar.update(current)

        # headers contains the necessary Content-Type and Content-Length
        # datagen is a generator object that yields the encoded parameters
        f = tempfile.NamedTemporaryFile(mode='wb', prefix='tmp_yhat_', delete=False)
        model_name = data['modelname'] + ".yhat"
        try:
            data = json.dumps(data)
        except UnicodeDecodeError, e:
            raise Exception("Could not serialize into JSON. String is not utf-8 encoded `%s`" % str(e.args[1]))
        zlib_compress(data, f)
        f.close()

        datagen, headers = multipart_encode({model_name: open(f.name, "rb")}, cb=progress)

        url = self.base_uri + endpoint + "?" + urllib.urlencode(params)
        req = urllib2.Request(url, datagen, headers)
        auth = '%s:%s' % (params['username'], params['apikey'])
        base64string = base64.encodestring(auth).replace('\n', '')
        req.add_header("Authorization", "Basic %s" % base64string)
        # Actually do the request, and get the response
        try:
            response = urllib2.urlopen(req)
        except urllib2.HTTPError, e:
            if e.code > 200:
                responseText = e.read()
                sys.stderr.write("\nDeployment error: " + responseText)
                return { "status": "error", "message": responseText }
            else:
                sys.stderr.write("\nError in HTTP connection")
                return { "status": "error", "message": "Error in HTTP connection." }
        except Exception, e:
            sys.stderr.write("\nDeployment error: " + str(e))
            return { "status": "error", "message": str(e) }
        rsp = response.read()
        pbar.finish()
        # clean up after we're done
        os.remove(f.name)
        reply = {
            "status": "OK",
            "message": "Model successfully uploaded. Your model will begin building momentarily. Please see %s for more details" % self.base_uri
        }
        return reply

class Yhat(API):

    """
    A connection to the Yhat API

    Parameters
    ----------
    username: string
        your Yhat username
    apikey: string
        your Yhat apikey
    uri: string
        your Yhat server URL (i.e. http://cloud.yhathq.com/)
    """

    def __init__(self, username, apikey, uri):
        self.username = username
        self.apikey = apikey
        if uri.endswith("/") is False:
            uri += "/"
        self.ws = None
        self.base_uri = uri
        self.headers = {'Content-Type': 'application/json'}
        self.q = {"username": self.username, "apikey": apikey}
        if self.base_uri != BASE_URI:
            e = self._authenticate()
            if e is not None:
                raise Exception("Failed to authenticate: %s" % e)

    def _check_obj_size(self, obj):
        """
        Checks if an object is greater than 50 MB

        Parameters
        ----------
        obj: object
            any object

        Returns
        -------
        boolean
        """
        if self.base_uri != BASE_URI:
            # not deploying to the cloud so models can be as big as you want
            if sys.getsizeof(obj) > 52428800:
                return False
        elif sys.getsizeof(obj) > 52428800:
            raise Exception("Sorry, your file is too big for a free account.")

        return True

    def _authenticate(self):
        """
        Returns
        -------
        error: None or Exception
            verifies your API credentials are valid
        """
        try:
            response = self._post('verify', self.q, {})
            error = response["success"]
            return None
        except Exception, e:
            return e

    def _convert_to_json(self, data):
        """
        Tries to convert data into a JSON frieldy dict.

        Parameters
        ----------
        data: object
            data to be converted to valid JSON

        Returns
        -------
        data: object
            same data, but compatible with JSON
        """
        try:
            import pandas as pd
        except ImportError:
            return data

        if isinstance(data, pd.DataFrame):
            data_values = data.transpose().to_json(
                orient='values', date_format='iso')
            data_values = json.loads(data_values)
            try:
                from collections import OrderedDict
                data = OrderedDict(zip(data.columns, data_values))
            except ImportError:
                data = dict(zip(data.columns, data_values))
        return data

    def predict(self, model, data, model_owner=None, raw_input=False):
        """
        Executes a single prediction via the Yhat API.

        Parameters
        ----------
        model: string
            the name of your model
        data: dictionary/data frame
            data required to make a single prediction. this can be a dict or
            a dataframe
        model_owner: string
            username of the model owner for shared models. optional
        raw_input: bool
            whether or not to attempt to parse the incoming JSON. for calling R
            models only

        Returns
        -------
        data: dictionary
            data returned by a model
        """
        data = self._convert_to_json(data)
        q = self.q
        q['model'] = model
        if raw_input==True:
            q['raw_input'] = True
        model_user = self.username if model_owner is None else model_owner
        if self.base_uri != BASE_URI:
            endpoint = "%s/models/%s/" % (model_user, model)
        else:
            data = {"data": data}
            endpoint = 'predict'
        return self._post(endpoint, q, data)

    def _extract_model(self, name, model, session, autodetect, verbose=0):
        """
        Extracts source code and any objects required to deploy the model.

        Parameters
        ----------
        name: string
            name of your model
        model: YhatModel
            an instance of a Yhat model
        session: globals()
            your Python's session variables (i.e. "globals()")
        verbose: int
            log level
        """
        code = ""
        print "extracting model"

        if 1 == 2 and _get_source(YhatModel.execute) == _get_source(model.execute):
            msg = """'execute' method was not implemented.
            If you believe that you did implement the 'execute' method,
            check to make sure there isn't an indentation error."""
            raise Exception(msg)

        bundle = save_function(model, session, verbose=verbose)
        bundle["largefile"] = True
        bundle["username"] = self.username
        bundle["language"] = "python"
        bundle["modelname"] = name
        bundle["className"] = model.__name__
        bundle["code"] = code + "\n" + bundle.get("code", "")

        # REQUIREMENTS
        if DETECT_REQUIREMENTS and autodetect:
            requirements = getImplicitRequirements(model, session)
        else:
            requirements = getExplicitRequirmets(model, session)
        bundle["reqs"] = requirements

        # MODULES
        modules = bundle.get("modules", [])
        if modules:
            print "model source files"
            for module in modules:
                name = module["name"]
                parent_dir = module.get("parent_dir", "")
                if parent_dir != "":
                    name = os.path.join(parent_dir, name)
                print " [+]", name

        # OBJETCS
        objects = bundle.get("objects", {})
        if objects:
            print "model variables"
            for name, pkl in objects.iteritems():
                try:
                    obj = terragon.loads_from_base64(pkl)
                    t = type(obj)
                    del obj
                except Exception as e:
                    print "ERROR pickling object:", name
                    raise e
                size = 3. * float(len(pkl)) / 4.
                print " [+]", name, t, sizeof_fmt(size)

        return bundle

    def deploy(self, name, model, session, sure=False, packages=[], patch=None, dry_run=False, verbose=0, autodetect=True):
        """
        Deploys your model to a Yhat server

        Parameters
        ----------
        name: string
            name of your model
        model: YhatModel
            an instance of a Yhat model
        session: globals()
            your Python's session variables (i.e. "globals()")
        sure: boolean
            if true, then this will force a deployment (like -y in apt-get).
            if false or blank, this will ask you if you're sure you want to
            deploy
        autodetect: flag for using the requirement auto-detection feature.
            if False, you should explicitly state the packages required for
            your model, or it may not run on the server.
        """
        # first let's check and make sure the user actually wants to deploy
        # a new version
        if not re.match("^[A-Za-z0-9_]+$", name):
            raise Exception("Model name must only contain: [A-Za-z0-9_]")
        if not isinstance(packages, list):
            raise Exception(
                "`packages` must be a list of ubuntu packages to install")
        if (not sure) and (not dry_run):
            sure = raw_input("Are you sure you want to deploy? (y/N): ")
            if sure.lower() != "y":
                print "Deployment canceled"
                sys.exit()
        bundle = self._extract_model(name, model, session, verbose=verbose, autodetect=autodetect)
        bundle['packages'] = packages
        if isinstance(patch, str)==True:
            patch = "\n".join([line.strip() for line in patch.strip().split('\n')])
            bundle['code'] = patch + "\n" + bundle['code']

        if dry_run:
            return {"status": "ok", "info": "dry run complete"}
        if self._check_obj_size(bundle) is False:
            # we're not going to deploy; model is too big, but let's give the
            # user the option to upload it manually
            raise Exception("Model is too large to deploy over HTTP")
        else:
            # upload the model to the server
            data = self._post_file("deployer/model/large", self.q, bundle, pb=True)
            return data


def zlib_compress(data, to):
    step = 4 << 20 # 4MiB
    c = zlib.compressobj()

    for i in xrange(0, len(data), step):
        to.write(c.compress(data[i:i+step]))

    to.write(c.flush())
