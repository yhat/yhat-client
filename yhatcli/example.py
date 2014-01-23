from io.save_session import save_function
import json
import sys


def parse_json(somejson):
    try:
        return json.loads(somejson)
    except Exception, e:
        print "Input was not valid JSON."
        print "==> %s" % str(e)

class MyModel(object):
    def execute(self):
        pass

    def test_locally(self, newdata):
        pass

    def run(self):
        print "paste test data into terminal"
        print "Paste your test data here"
        print "Data should be formatted as valid JSON."
        print "Hit <ENTER> to execute your model after pasting in data"
        while True:
            data = sys.stdin.readline()
            data = parse_json(data)
            print "executing =>", data


if __name__ == '__main__':
    MyModel().run()
