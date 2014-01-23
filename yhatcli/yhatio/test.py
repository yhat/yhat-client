import json
import pickle
from sklearn.datasets.base import load_iris
# code for <function pred at 0x1050aa140>
def pred(data):
    return clf.predict(load_iris().data)

pickles = json.load(open('pred.json', 'rb'))
for varname, pickled_value in pickles.get('objects', {}).items():
    globals()[varname] = pickle.loads(pickled_value)
    
print pred(100)
