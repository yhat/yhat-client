from yhatio.input_and_output import preprocess
from yhatio.models import YhatModel
import pandas as pd
import json
import pickle


# code for <class '__main__.MyModel'>
class MyModel(YhatModel):
    @preprocess(out_type=pd.DataFrame)
    def execute(self, data):
        return predict(data)

# code for <function predict at 0x10c7d41b8>
def predict(df):
    y = MyOtherClass()
    print y.hello("from the predict function")
    pred = clf.predict(df)
    return pred

class MyOtherClass:
    def hello(self, x):
        return "hello: %s" % str(x)


pickles = json.load(open('mymodel.json', 'rb'))
for varname, pickled_value in pickles.get('objects', {}).items():
    globals()[varname] = pickle.loads(pickled_value)
    

print MyModel().execute({"x": 1, "z": 10})