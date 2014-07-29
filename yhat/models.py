import urllib2
import base64
import json

from .credentials import read
from colorama import init
from colorama import Fore
from elastictabstops import Table

init()


def create_request(uri, username, apikey):
    request = urllib2.Request(uri)
    auth = base64.encodestring("%s:%s" % (username, apikey)).replace("\n", "")
    request.add_header("Authorization", "Basic %s" % auth)

    try:
        r = urllib2.urlopen(request)
    except urllib2.URLError, e:
        if hasattr(e, 'reason'):
            print Fore.RED + 'We failed to reach a server.'
            print Fore.RED + 'Reason: ', e.reason
        elif hasattr(e, 'code'):
            print Fore.RED + 'The server couldn\'t fulfill the request.'
            print Fore.RED + 'Error code: ', e.code

        print Fore.RESET
        return None
    else:
        return json.load(r)


def get_status(username, apikey, server, owner, modelname):
    request_uri = "%s/users/%s/models/%s/status" % (
        server, owner, modelname)
    resp = create_request(request_uri, username, apikey)

    if 'error' in resp:
        print Fore.RED + resp["message"] + Fore.RESET
        return None

    return resp["status"]


def get(modelname=None, admin=False):
    creds = read()
    if admin and modelname is None:
        request_uri = "%s/models" % (creds["server"])
    elif modelname is None:
        request_uri = "%s/users/%s/models" % (
            creds["server"], creds["username"])
    else:
        request_uri = "%s/users/%s/models/%s" % (
            creds["server"], creds["username"], modelname)
    models = create_request(request_uri, creds["username"], creds["apikey"])

    if isinstance(models, (list, tuple)):
        if not models:
            print Fore.RED + "No models found for " \
                + creds["username"] + " on " + creds["server"] + Fore.RESET
            return None
    else:
        if 'error' in models:
            print Fore.RED + models["message"] + Fore.RESET
            return None
        models = [models]

    for model in models:
        if 'owner' in model:
            owner = model["owner"]
        else:
            owner = creds["username"]
        model["status"] = get_status(creds["username"],
                                     creds["apikey"],
                                     creds["server"],
                                     owner,
                                     model["name"])
    return models


def table(models, admin=False):
    if admin is False:
        creds = read()
        owner = str(creds["username"])

    if models is not None:
        model_table = []
        model_table.append(
            ['NAME', 'USERNAME', 'LANG', 'VERSIONS', 'LAST UPDATED', 'STATUS'])

        for model in models:
            status = str(model["status"])
            if status == "online":
                status = Fore.GREEN + status + Fore.RESET
            elif status == "building":
                status = Fore.CYAN + status + Fore.RESET
            elif status == "built":
                status = Fore.YELLOW + status + Fore.RESET
            elif status == "failed":
                status = Fore.RED + status + Fore.RESET

            if admin:
                owner = str(model["owner"])
            model_table.append([str(model["name"]),
                                owner,
                                str(model["lang"]),
                                str(model["versions"]),
                                str(model["friendly_date"]),
                                status])
        return Table(model_table).to_spaces()
