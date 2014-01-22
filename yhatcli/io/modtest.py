import pickle
import json
from requests import Session
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVC
from sklearn.datasets import load_iris


def saywhat(i):
    print i

class MyClass:
    def hello(self, x):
        y = saywhat("?")
        return str(x) + " Hello!"

def goodbye():
    z = Session()
    return pickle.dumps(10)

z = range(10)
def hello(x):
    y = 100
    q = goodbye()
    t = MyClass()
    x = "%s %d" % (t.hello(10), sum(z) * y)
    return t.hello(x)


from model import spider_function

iris = load_iris()

clf = SVC()
clf.fit(iris.data, iris.target)

def pred(data):
    return clf.predict(iris.data)

# print spider_function(goodbye, globals())
# print spider_function(hello, globals())
source_code, pickles = spider_function(pred, globals())
source_code = "import pickle\n" + source_code
print source_code
with open("data.json", "wb") as f:
    json.dump(pickles, f)


