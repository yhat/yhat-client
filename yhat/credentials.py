import json
import base64
import os
import re
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
    _username = ""
    _apikey = ""
    _server = " [%s]" % "http://cloud.yhathq.com"
    if has():
        creds = read()
        _username = " [%s]" % creds["username"]
        _apikey = " [%s]" % creds["apikey"]
        _server = " [%s]" % creds["server"]
    username = raw_input("Yhat username" + _username + ": ")
    apikey = raw_input("Yhat apikey" + _apikey + ": ")
    server = raw_input("Yhat server" + _server + ": ")

    if username == "":
        username = re.search(r"[^[]*\[([^]]*)\]", _username).group(1)
    if apikey == "":
        apikey = re.search(r"[^[]*\[([^]]*)\]", _apikey).group(1)

    if server == "":
        server = re.search(r"[^[]*\[([^]]*)\]", _server).group(1)
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
