# Yhat Python Client
This is the connection to the Yhat API. If you'd like to read more, [visit our
docs](http://docs.yhathq.com/).

## [Quickstart](http://docs.yhathq.com/python/tutorial)
You can download the example [here](https://s3.amazonaws.com/yhat-examples/beer-recommender.zip)
, or clone the git repo.

```bash
$ git clone git@github.com:yhat/yhat-examples.git
$ cd beer-recommender
```

Insert your APIKEY and USERNAME and run the script.
```bash
$ python recommender.py
Deploy? (y/N): y
# {"status": "success"}
```

## Overview

## Usage

### Installation
Using `pip`:

```bash
$ pip install --upgrade yhat
```

From source:

```bash
$ git clone git@github.com:yhat/yhat-client.git
$ cd yhat-client
$ python setup.py install
```

### Setting up your model

### Handling Input and Output

#### `df` to `df`
Specify `df` to `df` by decorating `execute` with the following:
```python
from yhat import preprocess
# ...
# ...
@preprocess(in_type=pd.DataFrame, out_type=pd.DataFrame)
def execute(self, data)
# ...
# ...
```

#### Input
```js
// making 1 prediction with an API call
{
  "column1": VALUE,
  "column2": VALUE
}
// making multiple predictions with 1 API call
{
  "column1": [ VALUE_1, VALUE_2 ]
  "column2": [ VALUE_1, VALUE_2 ]
}
```
#### Output
Data will come back with columns as keys and values as lists of values.
```js
{
  "output_column1": [ VALUE_1 ],
  "output_column2": [ VALUE_1 ]
}
```

### `df` to `dict`
```python
from yhat import preprocess
# ...
# ...
@preprocess(in_type=pd.DataFrame, out_type=dict)
def execute(self, data)
# ...
# ...
```

#### Input
```js
// making 1 prediction with an API call
{
  "column1": VALUE,
  "column2": VALUE
}
// making multiple predictions with 1 API call
{
  "column1": [ VALUE_1, VALUE_2 ]
  "column2": [ VALUE_1, VALUE_2 ]
}
```
#### Output
Selecting the `dict` output gives the user the ability to define their own
output format (so long as it is a valid Python dictionary.
```js
// this is valid
{
  "pred": 1
  "values": [1, 2, 3]
}
// this is also valid
{
  "x": {
    "y": 10
  "z": 100
  }
}
```

### `dict` to `dict`
This is the most "free form" means of input and output. The user can send in any
valid dictionary, process it how they like, and then return any valid dictionary
.
```python
from yhat import preprocess
# ...
# ...
@preprocess(in_type=dict, out_type=dict)
def execute(self, data)
# ...
# ...
```

#### Input
```js
// this is valid
{
  "pred": 1
  "values": [1, 2, 3]
}
// this is also valid
{
  "x": {
    "y": 10
  },
    "z": 100
  }
}
```
#### Output
```js
// this is valid
{
  "pred": 1
  "values": [1, 2, 3]
}
// this is also valid
{
  "x": {
    "y": 10
  },
    "z": 100
  }
}
```

### Deploying

```python
>>> yh.deploy("myExampleModel", MyExampleModel, globals())
```

## Examples

- [Hello World](http://docs.yhathq.com/python/examples/hello-world)
- [Hello pip](http://docs.yhathq.com/python/examples/hello-pip)
- [Step Model](http://docs.yhathq.com/python/examples/stepmodel)
- [Random Forest](http://docs.yhathq.com/python/examples/random-forest)
- [Twitter Feed](http://docs.yhathq.com/python/examples/twitter-feed)

## Misc

## Dependencies

*Required*

- doctopt
- progressbar
- pip
- Flask
- colorama
- websocket-client
- ElasticTabstops
- dill

*Highly suggested*

- pandas
- sklearn


[![Analytics](https://ga-beacon.appspot.com/UA-46996803-1/yhat-client/README.md)](https://github.com/yhat/yhat-client)

