from sklearn.linear_model import LinearRegression
from clean_data import training, training_no_price, dv

LR = LinearRegression().fit(dv.transform(training_no_price.T.to_dict().values()), training.price)

trainingErrs = abs(LR.predict(dv.transform(training.T.to_dict().values())) - training.price)