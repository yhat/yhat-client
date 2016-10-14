from __future__ import print_function

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

from builtins import input
from builtins import bytes
import sys
import warnings
import base64
import json
import pickle
import terragon
import inspect
import tempfile
import zlib
import re
import os
import os.path
import requests
from six import string_types
from requests_toolbelt.multipart.encoder import MultipartEncoderMonitor, MultipartEncoder
from progressbar import ProgressBar, Percentage, Bar, FileTransferSpeed, ETA

from .deployment.models import YhatModel
from .deployment.save_session import save_function, _get_source, reindent
from .utils import sizeof_fmt, is_valid_json

devnull = open(os.devnull, "w")

# If we can't import everything we need to detect requirements from
# this version of pip, then we just warn and turn off the feature.
getExplicitRequirements, getImplicitRequirements = None, None
try:
    from .requirements import getExplicitRequirements, getImplicitRequirements
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
            url = self.base_uri + endpoint + "?" + urlencode(params)
            auth = '%s:%s' % (params['username'], params['apikey'])
            base64string = base64.encodestring(auth).replace('\n', '')
            base64header = "Basic %s" % base64string
            headers = {
                'Content-Type': 'application/json',
                'Authorization': base64header
            }
            response = requests.get(url=url, headers=headers)
            rsp = response.text
            return json.loads(rsp)
        except Exception as e:
            raise e

    def _post(self, endpoint, params, data):
        """
        Parameters
        ----------
        endpoint: string
            name of the rest endpoint you want to hit
        params: dictionary
            querystring parameters for API call
        data: dictionary
            data you want transfered as JSON

        Returns
        -------
        data: dictionary
            whatever is returned by the API
        """
        if is_valid_json(data)==False:
            raise Exception("`data` is not valid JSON")

        url = self.base_uri + endpoint
        headers = { "Content-Type": "application/json"}
        username, apikey = params['username'], params['apikey']

        response = requests.post(url=url, headers=headers, data=data, params=params, auth=(username, apikey))
        if response.status_code > 200:
            # if we don't get a 200, write the error and raise an status Exception
            sys.stderr.write("error: " + response.text)
            response.raise_for_status()
        return response.json()

    def _post_file(self, endpoint, params, data, pb=True):

        # headers contains the necessary Content-Type and Content-Length
        # datagen is a generator object that yields the encoded parameters
        f = tempfile.NamedTemporaryFile(mode='wb', prefix='tmp_yhat_', delete=False)
        model_name = data['modelname'] + ".yhat"
        try:
            data = json.dumps(data)
        except UnicodeDecodeError as e:
            raise Exception("Could not serialize into JSON. String is not utf-8 encoded `%s`" % str(e.args[1]))
        zlib_compress(data, f)
        f.close()

        def createCallback(encoder):
            # Stuff for progress bar setup
            widgets = ['Transfering Model: ', Bar(), Percentage(), ' ', ETA(), ' ', FileTransferSpeed()]
            pbar = ProgressBar(max_value=encoder.len, widgets=widgets).start()
            def callback(monitor):
                current = monitor.bytes_read
                pbar.update(current)
            return callback

        encoder = MultipartEncoder(
            fields={'model_name': (open(f.name, 'rb'))}
        )

        username, apikey = params['username'], params['apikey']
        headers = {'Content-Type': encoder.content_type,}

        callback = createCallback(encoder)
        monitor = MultipartEncoderMonitor(encoder, callback)
        url = self.base_uri + endpoint

        # Actually do the request, and get the response
        try:
            r = requests.post(url=url, data=monitor, headers=headers, params=params, auth=(username, apikey))
            if r.status_code != requests.codes.ok:
                r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            if r.status_code > 200:
                responseText = r.text
                sys.stderr.write("\nDeployment error: " + responseText)
                return { "status": "error", "message": responseText }
            else:
                sys.stderr.write("\nError in HTTP connection")
                return { "status": "error", "message": "Error in HTTP connection." }
        except Exception as err:
            sys.stderr.write("\nDeployment error: " + str(err))
            return { "status": "error", "message": str(err) }
        rsp = r.text
        # clean up after we're done
        f.close()
        os.unlink(f.name)
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
                raise Exception("Failed to authenticate: {}".format(e))

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
        except Exception as e:
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
                data = OrderedDict(list(zip(data.columns, data_values)))
            except ImportError:
                data = dict(list(zip(data.columns, data_values)))

        data = json.dumps(data)
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
        if raw_input==True:
            q['raw_input'] = True
        model_user = self.username if model_owner is None else model_owner
        if self.base_uri != BASE_URI:
            endpoint = "%s/models/%s/" % (model_user, model)
        else:
            data = {"data": data}
            endpoint = 'predict'
        return self._post(endpoint, q, data)

    def _extract_model(self, name, model, session, autodetect, is_tensorflow=False, verbose=0):
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
        print("extracting model")

        bundle = save_function(model, session, verbose=verbose)
        bundle["largefile"] = True
        bundle["username"] = self.username
        bundle["language"] = "python"
        bundle["modelname"] = name
        bundle["className"] = model.__name__
        bundle["code"] = code + "\n" + bundle.get("code", "")

        # REQUIREMENTS
        if DETECT_REQUIREMENTS and autodetect and getImplicitRequirements:
            requirements = getImplicitRequirements(model, session)
        elif getExplicitRequirements:
            requirements = getExplicitRequirements(model, session)
        else:
            requirements = "\n".join(getattr(model, "REQUIREMENTS", []))

        bundle["reqs"] = requirements

        # MODULES
        modules = bundle.get("modules", [])
        if modules:
            print("model source files")
            for module in modules:
                name = module["name"]
                parent_dir = module.get("parent_dir", "")
                if parent_dir != "":
                    name = os.path.join(parent_dir, name)
                print(" [+]", name)

        # OBJECTS
        objects = bundle.get("objects", {})
        if objects:
            print("model variables")
            for name, pkl in objects.items():
                if name=='__tensorflow_session':
                    continue
                try:
                    try:
                        obj = terragon.loads_from_base64(pkl)
                    except:
                        obj = terragon.loads_spark_from_base64(session['sc'], pkl)
                    t = type(obj)
                    del obj
                except Exception as e:
                    print("ERROR pickling object:", name)
                    raise e
                size = 3. * float(len(pkl)) / 4.
                print(" [+]", name, t, sizeof_fmt(size))

        if is_tensorflow==True:
            bundle['objects']['__tensorflow_session'] = terragon.sparkle.save_tensorflow_graph(session['sess'])

        return bundle

    def deploy(self, name, model, session, sure=False, packages=[], patch=None, dry_run=False, verbose=0, autodetect=True, is_tensorflow=False):
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
        packages: list (deprecated in ScienceOps 2.7.x)
            this is being deprecated in favor of custom runtime images
        sure: boolean
            if true, then this will force a deployment (like -y in apt-get).
            if false or blank, this will ask you if you're sure you want to
            deploy
        verbose: int
            Relative amount of logging info to display (higher = more logs)
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
            sure = str(input("Are you sure you want to deploy? (y/N): "))
            if sure.lower() != "y":
                print("Deployment canceled")
                sys.exit()
        bundle = self._extract_model(name, model, session, verbose=verbose, autodetect=autodetect, is_tensorflow=is_tensorflow)
        bundle['packages'] = packages
        if isinstance(patch, string_types) == True:
            patch = "\n".join([line.strip() for line in patch.strip().split('\n')])
            bundle['code'] = patch + "\n" + bundle['code']

        if dry_run:
            return {"status": "ok", "info": "dry run complete"}, bundle
        if self._check_obj_size(bundle) is False:
            # we're not going to deploy; model is too big, but let's give the
            # user the option to upload it manually
            raise Exception("Model is too large to deploy over HTTP")
        else:
            # upload the model to the server
            data = self._post_file("deployer/model/large", self.q, bundle, pb=True)
            return data

    def deploy_tensorflow(self, name, model, session, sess, sure=False, packages=[], patch=None, dry_run=False, verbose=0, autodetect=True):
        """
        Deploys a TensorFlow model to a Yhat server. This is a special case of deploy.

        Parameters
        ----------
        name: string
            name of your model
        model: YhatModel
            an instance of a Yhat model
        session: globals()
            your Python's session variables (i.e. "globals()")
        sess: tensorflow.Session, tensorflow.InteractiveSession
            your tensorflow session. this is typically `sess`
        packages: list (deprecated in ScienceOps 2.7.x)
            this is being deprecated in favor of custom runtime images
        sure: boolean
            if true, then this will force a deployment (like -y in apt-get).
            if false or blank, this will ask you if you're sure you want to
            deploy
        verbose: int
            Relative amount of logging info to display (higher = more logs)
        autodetect: flag for using the requirement auto-detection feature.
            if False, you should explicitly state the packages required for
            your model, or it may not run on the server.
        """

        try:
            model.setup_tf
        except:
            raise Exception("tensorflow models must have a `setup_tf` function")

        if 'sess' not in session:
            session['sess'] = sess

        src = "\n".join(inspect.getsource(model.setup_tf).split('\n')[1:])
        patch = "print('loading tensorflow session...')\n"
        patch += reindent(src)
        patch += "sess, _ = __terragon.sparkle.load_tensorflow_graph(__bundle['objects']['__tensorflow_session'])\n"
        patch += "print('done!')\n\n"

        return self.deploy(name, model, session, sure=sure, packages=packages,
            patch=patch, dry_run=dry_run, verbose=verbose, autodetect=autodetect, is_tensorflow=True)

    def deploy_spark(self, name, model, session, sc, sure=False, packages=[], patch=None, dry_run=False, verbose=0, autodetect=True):
        """
        Deploys a Spark model to a Yhat server. This is a special case of deploy.

        Parameters
        ----------
        name: string
            name of your model
        model: YhatModel
            an instance of a Yhat model
        session: globals()
            your Python's session variables (i.e. "globals()")
        sc: SparkContext
            your SparkContext. this is typically `sc`
        packages: list (deprecated in ScienceOps 2.7.x)
            this is being deprecated in favor of custom runtime images
        sure: boolean
            if true, then this will force a deployment (like -y in apt-get).
            if false or blank, this will ask you if you're sure you want to
            deploy
        verbose: int
            Relative amount of logging info to display (higher = more logs)
        autodetect: flag for using the requirement auto-detection feature.
            if False, you should explicitly state the packages required for
            your model, or it may not run on the server.
        """
        if 'sc' not in session:
            session['sc'] = sc

        patch = "from pyspark import SparkContext\n"
        patch += "sc = SparkContext()\n"
        patch += "sc.setLogLevel('ERROR')\n"

        return self.deploy(name, model, session, sure=sure, packages=packages,
            patch=patch, dry_run=dry_run, verbose=verbose, autodetect=autodetect)

def zlib_compress(data, to):
    step = 4 << 20 # 4MiB
    c = zlib.compressobj()
    data = bytes(data, "utf-8")
    for i in range(0, len(data), step):
        to.write(c.compress(data[i:i+step]))

    to.write(c.flush())
