from yhat import BaseModel, Yhat
from fit import dv, LR, trainingErrs
from load_data import testing
import numpy as np

class PricingModel(BaseModel):
    def transform(self, doc):
        """
        Maps input dict (from json post) into numpy array
        delegates to DictVectorizer self.dv
        """
        return self.dv.transform(doc)
    def predict(self, x):
        """
        Evaluate model on array
        delegates to LinearRegression self.lr
        returns a dict (will be json encoded) suppling 
        "predictedPrice", "suspectedOutlier", "x", "threshold" 
        where "x" is the input vector and "threshold" is determined 
        whether or not a listing is a suspected outlier.
        """
        doc = self.dv.inverse_transform(x)[0] 
        predicted = self.lr.predict(x)[0]
        err = abs(predicted - doc['price'])
        return {'predictedPrice': predicted, 
                'x': doc, 
                'suspectedOutlier': 1 if (err > self.threshold) else 0,
                'threshold': self.threshold}


pm = PricingModel(dv=dv, lr=LR, threshold=np.percentile(trainingErrs, 95))
print pm.execute(testing.T.to_dict()[0])

if raw_input("Deploy? (y/N): ").lower()=="y":
    username = "greg"
    apikey = "abcd1234"
    yh = Yhat(username, apikey, "http://cloud.yhathq.com/")
    print yh.deploy(model_name, fitted_model)