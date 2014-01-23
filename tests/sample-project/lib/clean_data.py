from load_data import training, training_no_price
from sklearn.feature_extraction import DictVectorizer


dv = DictVectorizer()
dv.fit(training.T.to_dict().values())
print dv.feature_names_



