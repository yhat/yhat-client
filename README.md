# Yhat Python Client
This is the connection to the Yhat API. If you'd like to read more, [visit our
docs](http://docs.yhathq.com/).

**Table of Contents:**

- [Quickstart](#quickstart)
- [Installation](#installation)
- [Overview](#overview)
  - [Handling Input and Output](#handling-input-and-output)
  - [Deploying](#deploying)
  - [Examples](#examples)
- [yhat-cli](#yhat-cli)
- [Dependencies](#dependencies)


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


## Installation
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

[![Analytics](https://ga-beacon.appspot.com/UA-46996803-1/yhat-client/README.md)](https://github.com/yhat/yhat-client)
