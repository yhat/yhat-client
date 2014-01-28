from requests import Session
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVC
from sklearn.datasets import load_iris

from anothermod import again 

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


from save_session import save_function

iris = load_iris()

clf = SVC()
clf.fit(iris.data, iris.target)

def pred(data):
    print again(100)
    return clf.predict(load_iris().data)

#####                             #####
#####  This is the actual process #####
#####                             #####

import json
print json.dumps(save_function(pred, globals()))
