import warnings
from math import log

try:
    import numpy as np
except Exception, e:
    warnings.warn("Warning: numpy required to auto-document models!")


def isnumeric(x):
    try:
        x += 1
        return True
    except:
        return False


def document_column(df, col):
    doc = {}
    doc["name"] = col
    if isnumeric(df[col]):
        doc["dtype"] = "number"
        doc["step"] = 0
        step = abs(max(df[col]) - min(df[col])) / 10 + 0.01
        doc["step"] = 10**round(log(step, 10) - log(5.5, 10) + 0.5)
        doc["palceholder"] = np.median(df[col])
    elif (len(np.unique(df[col])) / float(len(df))) < 0.25:
        doc["dtype"] = "factor"
        doc["levels"] = sorted(np.unique(df[col]))
    else:
        doc["dtype"] = "text"
    return doc

def document_data(df):
    docs = []
    for col in df.columns:
        docs.append(document_column(df, col))
    return docs