import schema
import json


mySchema = {
    "name": schema.And(str, lambda x: x in ('Greg', 'Jeff')),
    "n": int
}


data = { "name": "Greg", "n": 1 }
print schema.Schema(mySchema).validate(data)

mySchema = {
    "name": str
}

data = { "name": "paul" }
print schema.Schema(mySchema).validate(data)

mySchema = {
    "name": [str]
}

data = { "name": ["paul"] }
print schema.Schema(mySchema).validate(data)


mySchema = {
    "a": float,
    "b": float,
    "c": float
}

data = { "a": 1., "b": 2., "c": 3.}
print schema.Schema(mySchema).validate(data)
data = { "a": 1, "b": 2, "c": 3}
print schema.Schema(mySchema).validate(data)
