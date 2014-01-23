import pandas as pd

training = pd.read_csv('data/accord_sedan_training.csv')
testing = pd.read_csv('data/accord_sedan_testing.csv')

training_no_price = training.drop(['price'], 1)
