from yhat import Yhat, BaseModel
import pprint as pp
import requests
import json
import pickle



# raw_data = [[  0.,   0.,   5.,  13.,   9.,   1.,   0.,   0.],
#            [  0.,   0.,  13.,  15.,  10.,  15.,   5.,   0.],
#            [  0.,   3.,  15.,   2.,   0.,  11.,   8.,   0.],
#            [  0.,   4.,  12.,   0.,   0.,   8.,   8.,   0.],
#            [  0.,   5.,   8.,   0.,   0.,   9.,   8.,   0.],
#            [  0.,   4.,  11.,   0.,   1.,  12.,   7.,   0.],
#            [  0.,   2.,  14.,   5.,  10.,  12.,   0.,   0.],
#            [  0.,   0.,   6.,  13.,  10.,   0.,   0.,   0.]]

yh = Yhat("greg", "MWFAJnAn4hhd531MWrNpE6hQeiwX0HsB7PdB1d1aEhw", "http://localhost:5000/")
# yh = Yhat("greg", "MWFAJnAn4hhd531MWrNpE6hQeiwX0HsB7PdB1d1aEhw")

# pp.pprint(skd.show_models())
# print "*"*80
# pp.pprint(skd.raw_predict('irisTree', [2, 3, 2, 2]))
# print "*"*80
# pp.pprint(skd.predict('digits', raw_data))
# print "*"*80


class DecisionTreePML(BaseModel):
    def transform(self, rawData):
        pair = [2, 3]
        data = np.array(rawData)
        X = data[:, pair]
        mean = self.xtrain.mean(axis=0)
        std = self.xtrain.std(axis=0)
        X = (X - mean) / std
        return X

    def predict(self, data):
        pred = self.clf.predict(data).tolist()
        return pred

clf = pickle.load(open('./yhat/test/decisiontree.model', 'rb'))
xtrain = pickle.load(open('./yhat/test/xtrain.model', 'rb'))

myTree = DecisionTreePML(clf=clf, xtrain=xtrain)



pp.pprint(yh.upload("gregsTree", myTree))














