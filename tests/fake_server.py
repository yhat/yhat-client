from flask import Flask
app = Flask(__name__)

@app.route('/<path:path>', methods=["GET", "POST"])
def catch_all(path):
    return "You send a request to: %s" % path, 408

if __name__ == '__main__':
    app.run()
