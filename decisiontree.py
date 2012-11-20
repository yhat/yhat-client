import numpy as np
import pylab as pl

from sklearn.datasets import load_iris
from sklearn.tree import DecisionTreeClassifier

from skdeploy import Skdeploy
from skdeploy.pml import PML

# Load data
iris = load_iris()
X = iris.data
y = iris.target


# Standardize
mean = X.mean(axis=0)
std = X.std(axis=0)
xRaw = X
X = (X - mean) / std

# Train
clf = DecisionTreeClassifier().fit(X, y)

class DecisionTreePML(PML):
    def transform(self, data):
        mean = self.Xraw.mean(axis=0)
        std = self.Xraw.std(axis=0)
        data = (data - mean) / std
        return X

    def predict(self, data):
        return self.clf.predict(data)


myDT = DecisionTreePML(clf=clf, xRaw=xRaw)

skd = Skdeploy("glamp", "abcd1234")

print skd.upload("gregsNewTree", myDT)