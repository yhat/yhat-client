# Yhat Python Client
This is the connection to the Yhat API. If you'd like to read more, [visit our 
docs](http://docs.yhathq.com/)

## [Quickstart](http://docs.yhathq.com/python/tutorial)

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


## Handling Input and Output

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

## Examples

- [Hello World](http://docs.yhathq.com/python/hello-world)
- [Hello pip](http://docs.yhathq.com/python/hello-pip)
- [Random Forest](http://docs.yhathq.com/python/random-forest)
- [Twitter Ranker](http://docs.yhathq.com/python/twitter-ranker)

## Misc

## Dependencies

*Required*

- progressbar
- pip
- Flask
- colorama
- websocket-client
- prettytable

*Highly suggested*

- pandas
- sklearn


[![Analytics](https://ga-beacon.appspot.com/UA-46996803-1/yhat-client/README.md)](https://github.com/yhat/yhat-client)

