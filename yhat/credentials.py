import json
import base64
import os


def setup():
    """
    Prompts the user for their credentials and the saves them to a Yhat "dot" file.
    """
    username = raw_input("Yhat username: ")
    apikey = raw_input("Yhat apikey: ")
    with open(os.path.join(os.environ['HOME'], '.yhat', '.config'), 'w') as f:
		data = json.dumps({"username": username, "apikey": apikey})
		data = base64.encodestring(data)
		f.write(data)

def read():
    """
    Extracts credentials from a "dot" file
    
    Returns
    =======
    credentials: dict
        your credentials in form:
        {"username": "YOUR USERNAME", "apikey": "YOUR APKIKEY}"
    """
    data = open(os.path.join(os.environ['HOME'], '.yhat', '.config')).read()
    return json.loads(base64.decodestring(data))

