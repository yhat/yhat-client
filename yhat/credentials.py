import json
import base64
import os
from urlparse import urlparse


def has():
    """
    Checks if the user has saved their credentials.
    """
    return os.path.isfile(os.path.join(os.environ['HOME'], '.yhat', '.config'))


def setup():
    """
    Prompts the user for their credentials and the saves them to a Yhat "dot"
    file.
    """
    username = raw_input("Yhat username: ")
    apikey = raw_input("Yhat apikey: ")
    server = raw_input("Yhat server: [http://cloud.yhathq.com] ")

    if server == "":
        server = "http://cloud.yhathq.com"
    else:
        if not "http://" in server and not "https://" in server:
            server = "http://" + server
        o = urlparse(server)
        server = "%s://%s" % (o.scheme, o.netloc)

    # create the directory if it doesn't exist
    yhat_dir = os.path.join(os.environ['HOME'], '.yhat')
    if not os.path.exists(yhat_dir):
        os.makedirs(yhat_dir)

    with open(os.path.join(yhat_dir, '.config'), 'w') as f:
        data = json.dumps({"username": username,
                           "apikey": apikey,
                           "server": server})
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
