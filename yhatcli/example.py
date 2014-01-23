### <Analysis START> ###
from sklearn.linear_model import LogisticRegression
from sklearn.datasets import load_iris
import pandas as pd
import json

# this is your new "BaseModel"
from yhatio.models import YhatModel
# these define you IO standards
from yhatio.input_and_output import df_to_df, df_to_dict, dict_to_dict
# i'm thinking the above get consolidated into this...
from yhatio.input_and_output import preprocess

clf = LogisticRegression()
x = pd.DataFrame({
    "x": [1, 2, 1, 3, 1, 2, 3, 1, 2],
    "y": [0, 1, 0, 1, 0, 1, 0, 1, 1],
    "z": [0, 2, 3, 2, 4, 2, 2, 4, 0]
})
clf.fit(x[['x', 'z']], x['y'])

def predict(df):
    pred = clf.predict(df)
    return pred
    return {"pred": pred}

### <Analysis END> ###

def fill_z(row):
    return 1 + row['x']

features = [
        {"name": "x", "na_filler": 0},
        {"name": "z", "na_filler": fill_z}
]


### <DEPLOYMENT START> ###
class MyModel(YhatModel):
    #@preprocess(in_type=dict, out_type=pd.DataFrame, null_handler=features)
    @preprocess(out_type=pd.DataFrame, null_handler=features)
    def execute(self, data):
        return predict(data)

# push to server would be here
# from yhatio.save_session import save_function
# save_function("mm.json", MyModel, globals())
# then would push mm.json to the server
### <DEPLOYMENT END> ###


data = {"x": 1, "z": None}


if __name__ == '__main__':
    import warnings
    warnings.simplefilter(action = "ignore")
    MyModel().run(json.dumps({"x": 1, "z": 2}))

