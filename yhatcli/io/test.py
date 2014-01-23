import json
import pickle
# code for <function pred at 0x104df1140>
def pred(data):
    return clf.predict(iris.data)

pickles = json.load(open('data.json', 'rb'))
for varname, pickled_value in pickles.items():
    globals()[varname] = pickle.loads(pickled_value)

