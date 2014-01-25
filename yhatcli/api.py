import sys
import base64
import json
import pickle
import urllib2, urllib
import types
import websocket
import uuid
import zlib
import re
import os

from yhatio.save_session import save_function

try:
    import pandas as pd
except:
    print "Could not import pandas"
    pass

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
    
    def post(self, endpoint, params, data):
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
array, try casting it to a list (x.tolist()). If you're still having trouble, 
read our help here: {URL}.""".format(URL="http://docs.yhathq.com/help/json")
                print msg
            response = urllib2.urlopen(req, data)
            rsp = response.read()
            return json.loads(rsp)
        except Exception, e:
            raise e
    
    def handshake(self, model_name):
        """
        Parameters
        ----------
        model_name: string
            name of the model you want to connect to

        Returns
        -------
        ws: WebSocket connection
            a connection to the model's WebSocketServer
        """
        ws_uri = "{BASE_URI}/{USERNAME}/models/{MODEL_NAME}/"
        ws_base = self.base_uri.replace("http://", "ws://")
        ws_uri = ws_uri.format(BASE_URI=ws_base, USERNAME=self.username,
                               MODEL_NAME=model_name)
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
    def __init__(self, username, apikey, uri=BASE_URI):
        self.username = username
        self.apikey = apikey
        if uri.endswith("/")==False:
            uri += "/"
        self.ws = None
        self.base_uri = uri
        self.headers = {'Content-Type': 'application/json'}
        self.q = {"username": self.username, "apikey": apikey}
        if self.base_uri!=BASE_URI:
            if self._authenticate()==False:
                raise Exception("Incorrect username/apikey!")

    def _check_obj_size(self, obj):
        """
        Parameters
        ----------
        obj: object
            any object

        Returns
        -------
        """
        if self.base_uri!=BASE_URI:
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
        authed: boolean
            verifies your API credentials are valid
        """
        response = self.post('verify', self.q, {})
        authed = True
        try: 
            error = response["success"];
        except Exception, e:
            authed = False
        return authed

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
        if isinstance(data, pd.DataFrame):
            data = data.to_dict('list')
        return data

    def predict(self, model, data):
        """
        Executes a single prediction via the Yhat API.

        Parameters
        ----------
        model: string
            the name of your model
        data: dictionary/data frame
            data required to make a single prediction. this can be a dict or
            a dataframe

        Returns
        -------
        data: dictionary
            data returned by a model
        """
        data = self._convert_to_json(data)
        q = self.q
        q['model'] = model
        if self.base_uri!=BASE_URI:
            endpoint = "%s/models/%s/" % (self.username, model)
        else:
            data = {"data": data}
            endpoint = 'predict'
        return self.post(endpoint, q, data)
    
    def predict_ws(self, data):
        """
        
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
        if self.ws==None:
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

    def connect_to_socket(self, model):
        """
        Connects to the model's WebSocket endpoint. This is a pre-requisite for
        making predictions via the WebSocketServer.

        model: string
            name of the model you want to connect to
        """
        self.ws = self.handshake(model)
    
    def deploy(self, name, model, session, sure=False):
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
        if sure==False:
            sure = raw_input("Are you sure you want to deploy? (y/N): ")
            if sure.lower()!="y":
                print "Deployment canceled"
                sys.exit()
        # we're going to write the model out to a file and then transfer it
        filename = ".%s.yhat" % name
        bundle = save_function(filename, model, session)
        if self._check_obj_size(bundle)==False:
            # we're not going to deploy; model is too big
            pass
        else:
            # upload the model to the server
            # TODO: upload w/ a progress bar
            return self.post("deployer/model", self.q, bundle)


if __name__=="__main__":
    import pandas as pd
    df = pd.DataFrame({
        "x": range(10),
        "y": range(10)
    })
    yh = Yhat("blah", "blue")
    print yh._convert_to_json({"x": 1})
    print yh._convert_to_json(df)

    yh = Yhat("greg", "fCVZiLJhS95cnxOrsp5e2VSkk0GfypZqeRCntTD1nHA",
            "http://localhost:8080/")

    print yh.predict("mymodel", {"beer": "Coors Light"})
    yh.connect_to_socket("mymodel")
    print yh.predict_ws({"beer": "Coors Light"})
    for item in yh.yield_results():
        print item

