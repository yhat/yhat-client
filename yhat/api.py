import requests
import json
import pickle
import inspect

BASE_URI = "http://ec2-54-234-11-0.compute-1.amazonaws.com/"

class API(object):
    def __init__(self, base_uri):
        self.base_uri = base_uri

    def get(self, endpoint, params):
        try:
            return requests.get(self.base_uri + endpoint + "?", params=params).json
        except Exception, e:
            raise e
    
    def post(self, endpoint, params, data):
        try:
            return requests.post(self.base_uri + endpoint + "?",
                                 params=params,
                                 data=json.dumps(data)).json
        except Exception, e:
            raise e

class Yhat(API):
    def __init__(self, username, apikey):
        self.username = username
        self.apikey = apikey
        self.base_uri = BASE_URI
        self.q = {"username": self.username, "apikey": apikey}

    def show_models(self):
        return self.get("showmodels", self.q)

    def raw_predict(self, model, data):
        data = {"data": data}
        q = self.q
        q['model'] = model
        return self.post('predict', q, data)

    def predict(self, model, data):
        rawResponse = self.raw_predict(model, data)
        return rawResponse['prediction']

    def upload(self, modelname, pml):
        print "uploading...",
        try:
            className = pml.__class__.__name__
            filesource = "\n"
            filesource += "class %s(PML):" % className + "\n"
            filesource += inspect.getsource(pml.transform)+ "\n"
            filesource += inspect.getsource(pml.predict)
        except Exception, e:
            print
            print "Could not extract code. Either run script to compile a .pyc, or paste your code here."
            raw_input(":")
        userFiles = vars(pml)
        pickledUserFiles = {}
        for f, uf in userFiles.iteritems():
            pickledUserFiles[f] = pickle.dumps(uf)
        payload = {
            "modelname": modelname,
            "modelfiles": pickledUserFiles,
            "code": filesource,
            "className": className
        }

        rsp = self.post("model", self.q, payload)
        print "done!"
        return rsp











