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
    from requirements import merge
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

    def get(self, endpoint, params):
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

    def post(self, endpoint, params, data, pb=False):
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

    def post_file(self, endpoint, params, data, pb=True):
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
        filename = ".tmp_yhatmodel.yhat"
        model_name = data['modelname'] + ".yhat"
        with open(filename, "wb") as f:
            try:
                data = json.dumps(data)
            except UnicodeDecodeError, e:
                raise Exception("Could not serialize into JSON. String is not utf-8 encoded `%s`" % str(e.args[1]))
            data = zlib.compress(data)
            f.write(data)

        datagen, headers = multipart_encode({model_name: open(filename, "rb")}, cb=progress)

        url = self.base_uri + endpoint + "?" + urllib.urlencode(params)
        req = urllib2.Request(url, datagen, headers)
        auth = '%s:%s' % (params['username'], params['apikey'])
        base64string = base64.encodestring(auth).replace('\n', '')
        req.add_header("Authorization", "Basic %s" % base64string)
        # Actually do the request, and get the response
        response = urllib2.urlopen(req)
        rsp = response.read()
        pbar.finish()
        # clean up after we're done
        os.remove(filename)
        reply = {
            "status": "OK",
            "message": "Model successfully uploaded. Your model will begin building momentarily. Please see %s for more details" % self.base_uri
        }
        return reply

    def handshake(self, model_name, model_owner=None):
        """
        Parameters
        ----------
        model_name: string
            name of the model you want to connect to
        model_owner: string
            username of the model owner for shared models. optional

        Returns
        -------
        ws: WebSocket connection
            a connection to the model's WebSocketServer
        """
        ws_uri = "{BASE_URI}/{USERNAME}/models/{MODEL_NAME}/"
        ws_base = self.base_uri.replace("http://", "ws://")
        username = self.username if model_owner is None else model_owner
        ws_uri = ws_uri.format(BASE_URI=ws_base, USERNAME=username,
                               MODEL_NAME=model_name)
        ws_uri = "%s?username=%s&apikey=%s" % (ws_uri, self.username, self.apikey)
        ws = websocket.create_connection(ws_uri)
        auth = {
            "username": self.username,
            "apikey": self.apikey
        }
        ws.send(json.dumps(auth))
        return ws


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
            response = self.post('verify', self.q, {})
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
        return self.post(endpoint, q, data)

    def predict_ws(self, data):
        """

        Parameters
        ----------
        data: dictionary or data frame
            data required to make a single prediction. this can be a dict or
            a dataframe

        Returns
        -------
        id: string
            the id of the event; this will come in handy when it
            is receieved by the WebSocket client (remember, this is
            asynchronous)
        """
        if self.ws is None:
            msg = """In order to make predictions with WebScokets, you
need to connect to the server first. try running "connect_to_socket"
"""
            raise Exception(msg)
        data = self._convert_to_json(data)
        data['_id'] = str(uuid.uuid4())
        self.ws.send(json.dumps(data))
        return data['_id']

    def yield_results(self):
        """
        Listens to the WebSocket and awaits completed predictions

        Returns
        -------
        iterator: generator
            yields a new prediction
        """
        if self.ws is None:
            msg = """In order to make predictions with WebScokets, you
need to connect to the server first. try running "connect_to_socket"
"""
            raise Exception(msg)

        while True:
            yield self.ws.recv()

    def connect_to_socket(self, model, model_owner=None):
        """
        Connects to the model's WebSocket endpoint. This is a pre-requisite for
        making predictions via the WebSocketServer.

        model: string
            name of the model you want to connect to
        model_owner: string
            username of the model owner for shared models. optional
        """
        self.ws = self.handshake(model, model_owner)

    def _extract_model(self, name, model, session, verbose=0):
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
        # detect subclasses pickle errors by attempting to pickle all of the
        # objects in the global() session
        # http://stackoverflow.com/a/1948057/2325264
        # for k, v in session.items():
        #     try:
        #         terragon.dump(v, devnull)
        #     except terragon.pickle.PicklingError as e:
        #         try:
        #             base = type(v).__module__
        #             leaf = type(v).__class__.__name__
        #             parts = base.split(".")
        #             for i, _ in enumerate(parts):
        #                 importpath = ".".join(parts[:i+1])
        #                 globals()[importpath] = __import__(importpath)
        #             subclasses = []
        #             for attr in dir(v):
        #                 if attr.startswith("__"):
        #                     continue
        #                 if types.TypeType == type(getattr(v, attr)):
        #                     subclasses.append(attr)
        #             if not subclasses:
        #                 continue
        #             for c in subclasses:
        #                 truepath = ".".join([base, leaf, c])
        #                 code += "\n" + "\n".join([
        #                     "import " + base,
        #                     "setattr(sys.modules['%s'], '%s', %s)" % (base, ".".join([base, leaf]), truepath),
        #                 ])
        #         except Exception as e:
        #             print e
        #     except Exception as e:
        #         print e

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


        user_reqs = getattr(model, "REQUIREMENTS", "")
        if isinstance(user_reqs, basestring):
            user_reqs = [r for r in user_reqs.splitlines() if r]
        if user_reqs:
            print "model specified requirements"
            for r in user_reqs:
                if "==" not in r:
                    r = r + " (warning: unversioned)"
                print " [+]", r

        if DETECT_REQUIREMENTS:
            # Requirements auto-detection.
            bundle["reqs"] = "\n".join(
                str(r) for r in merge(session, getattr(model, "REQUIREMENTS", ""))
            )

        else:
            # The old way: REQUIREMENTS line.
            reqs = getattr(model, "REQUIREMENTS", "")
            if isinstance(reqs, list):
                reqs = '\n'.join(reqs)
            bundle["reqs"] = reqs

            # make sure we freeze Yhat so we're sure we're using the right version
            # this makes it a lot easier to upgrade the client
            import yhat
            bundle["reqs"] += '\n' + "yhat==" + yhat.__version__
            bundle["reqs"] = bundle["reqs"].strip().replace('"', '').replace("'", "")

        reqs = [r for r in bundle["reqs"].splitlines() if r]

        user_reqs_cmp = [user_req.lower() for user_req in user_reqs]
        detected_reqs = [r for r in reqs if r.lower() not in user_reqs_cmp]
        if detected_reqs:
            print "requirements automatically detected"
            for r in detected_reqs:
                print " [+]", r

        # print modules information
        modules = bundle.get("modules", [])
        if modules:
            print "model source files"
            for module in modules:
                name = module["name"]
                parent_dir = module.get("parent_dir", "")
                if parent_dir != "":
                    name = os.path.join(parent_dir, name)
                print " [+]", name

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

    def deploy(self, name, model, session, sure=False, packages=[], patch=None, dry_run=False, verbose=0):
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
        bundle = self._extract_model(name, model, session, verbose=verbose)
        bundle['packages'] = packages
        if isinstance(patch, str)==True:
            patch = "\n".join([line.strip() for line in patch.strip().split('\n')])
            bundle['code'] = patch + "\n" + bundle['code']

        if dry_run:
            return {"status": "ok", "info": "dry run complete"}
        if self._check_obj_size(bundle) is False:
            # we're not going to deploy; model is too big, but let's give the
            # user the option to upload it manually
            print "Model is too large to deploy over HTTP"
            should_we_deploy = raw_input(
                "Would you like to upload manually? (Y/n): ")
            if should_we_deploy.lower() == "y" or should_we_deploy == "":
                self.deploy_to_file(name, model, session)
        else:
            # upload the model to the server
            data = self.post_file("deployer/model/large", self.q, bundle, pb=True)
            return data

    def deploy_to_file(self, name, model, session, compress=True, packages=[], patch=None):
        """
        Bundles a local version of your model that can be manually uploaded to
        the server.

        Parameters
        ----------
        name: string
            name of your model
        model: YhatModel
            an instance of a Yhat model
        session: globals()
            your Python's session variables (i.e. "globals()")
        """
        if not re.match("^[A-Za-z0-9_]+$", name):
            raise Exception("Model name must only contain: [A-Za-z0-9_]")
        if not isinstance(packages, list):
            raise Exception(
                "`packages` must be a list of ubuntu packages to install")
        bundle = self._extract_model(name, model, session)
        bundle['apikey'] = self.apikey
        bundle['packages'] = packages
        if isinstance(patch, str)==True:
            patch = "\n".join([line.strip() for line in patch.strip().split('\n')])
            bundle['code'] = patch + "\n" + bundle['code']
        filename = "%s.yhat" % name
        with open(filename, "w") as f:
            bundle = json.dumps(bundle)
            if compress is True:
                bundle = zlib.compress(bundle)
            f.write(bundle)

        print "Model successfully bundled to file:"
        print "\t%s/%s.yhat" % (os.getcwd(), name)
        msg = "To deploy, visit %s and upload %s."
        upload_url = os.path.join(self.base_uri, "model", "upload")
        msg = msg % (upload_url, "%s.yhat" % name)
        print msg
        return filename

    def deploy_with_scp(self, name, model, sessions,
                        compress=True, packages=[], pem_path=None):
        if pem_path is None:
            raise Exception("Please specify your pem file for "
                            "authentication through the `pem_path` argument")
            return
        if not os.path.isfile(pem_path):
            raise Exception("No file found under '%s'" % pem_path)
        print "Deploying to file"
        filename = self.deploy_to_file(
            name, model, sessions, compress=compress, packages=packages)
        print "Sending over scp"
        http_re = re.compile("^http://")
        server_uri = http_re.sub("", self.base_uri.strip())
        server_uri = server_uri.strip("/")
        scp_cmd = "scp -i %s %s ubuntu@%s:~/" % (
            pem_path, filename, server_uri)
        subprocess.check_call(scp_cmd, shell=True)
        ssh_cmd = """ssh -i %s ubuntu@%s
        'sudo mv ~/%s
        /var/yhat/headquarters/uploads/'""" % (pem_path, server_uri, filename)
        subprocess.check_call(ssh_cmd, shell=True)
        os.remove(filename)
