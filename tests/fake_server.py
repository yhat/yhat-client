from flask import Flask
from flask import request
app = Flask(__name__)

@app.route('/verify', methods=["POST"])
def verify():
    username = request.args.get('username', '')
    apikey = request.args.get('apikey', '')
    print('username: ' + username)
    print('apikey: ' + apikey)
    return "{\"success\": \"true\"}", 200

@app.route('/<path:path>', methods=["GET", "POST"])
def catch_all(path):
    print(request)
    return "You send a request to: %s\n" % path, 200

if __name__ == '__main__':
    app.run()
