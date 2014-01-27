from sklearn.linear_model import LogisticRegression
from sklearn.datasets import load_iris
import pandas as pd
import json
import warnings
warnings.simplefilter(action = "ignore")

from yhat import YhatModel, Yhat, preprocess
from yhat import credentials


clf = LogisticRegression()
x = pd.DataFrame({
    "x": [1, 2, 1, 3, 1, 2, 3, 1, 2],
    "y": [0, 1, 0, 1, 0, 1, 0, 1, 1],
    "z": [0, 2, 3, 2, 4, 2, 2, 4, 0]
})
clf.fit(x[['x', 'z']], x['y'])

def fib(x):
    if x==0:
        return 1
    elif x==1:
        return 1
    return fib(x-1) + fib(x-2)

def predict(df):
    y = MyOtherClass()
    print y.hello("from the predict function")
    pred = clf.predict(df)
    x = fib(4)
    return pred

def predict_with_dict(df):
    pred = clf.predict(df)
    return {"pred": pred}

### <Analysis END> ###

def fill_z(row):
    return 1 + row['x']

features = [
        {"name": "x", "na_filler": 0},
        {"name": "z", "na_filler": fill_z}
]


class MyOtherClass:
    def hello(self, x):
        return "hello: %s" % str(x)

REQS = open("reqs.txt").read()

### <DEPLOYMENT START> ###
# @preprocess(in_type=dict, out_type=pd.DataFrame, null_handler=features)
class MyModel(YhatModel):
    REQUIREMENTS=REQS
    @preprocess(out_type=pd.DataFrame)
    def execute(self, data):
        return predict(data)

# "push" to server would be here

data = {"x": 1, "z": None}


if __name__ == '__main__':
    creds = credentials.read()
    yh = Yhat(creds['username'], creds['apikey'], "http://localhost:3000/")
    yh.deploy("mynewmodel", MyModel, globals())
    

