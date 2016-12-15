from yhat import Yhat, YhatModel
import unittest


class HelloWorld(YhatModel):
    def execute(self, data):
       me = data['name']
       greeting = "Hello %s!" % me
       return { "greeting": greeting }

class TestPython3Deployment(unittest.TestCase):

    def test_deployment(self):
        yh = Yhat("foo",  "bar", "http://api.yhathq.com/")
        _, bundle = yh.deploy("HelloWorld", HelloWorld, globals(), dry_run=True)
        self.assertTrue(True)

if __name__=="__main__":
    unittest.main()
