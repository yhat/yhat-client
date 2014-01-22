import json
import base64
import os


def setup():
	username = raw_input("Yhat username: ")
	apikey = raw_input("Yhat apikey: ")
	with open(os.path.join(os.environ['HOME'], '.yhat', '.config'), 'w') as f:
		data = json.dumps({"username": username, "apikey": apikey})
		data = base64.encodestring(data)
		f.write(data)

def read():
	data = open(os.path.join(os.environ['HOME'], '.yhat', '.config')).read()
	return json.loads(base64.decodestring(data))

