Yhat Python Client
==================

This is the connection to the Yhat API. If you'd like to read more,
`visit our docs <http://docs.yhathq.com/>`__.

**Table of Contents:**

-  `Quickstart <#quickstart>`__
-  `Installation <#installation>`__
-  `Overview <#overview>`__
-  `Handling Input and Output <#handling-input-and-output>`__
-  `Deploying <#deploying>`__
-  `Examples <#examples>`__
-  `yhat-cli <#yhat-cli>`__
-  `Dependencies <#dependencies>`__

`Quickstart <http://docs.yhathq.com/python/tutorial>`__
-------------------------------------------------------

You can download the example
`here <https://s3.amazonaws.com/yhat-examples/beer-recommender.zip>`__ ,
or clone the git repo.

.. code:: bash

    $ git clone git@github.com:yhat/yhat-examples.git
    $ cd beer-recommender

Insert your APIKEY and USERNAME and run the script.

.. code:: bash

    $ python recommender.py
    Deploy? (y/N): y
    # {"status": "success"}

Installation
------------

Using ``pip``:

.. code:: bash

    $ pip install --upgrade yhat

From source:

.. code:: bash

    $ git clone git@github.com:yhat/yhat-client.git
    $ cd yhat-client
    $ python setup.py install

Overview
--------

Handling Input and Output
~~~~~~~~~~~~~~~~~~~~~~~~~

``df`` to ``df``
^^^^^^^^^^^^^^^^

Specify ``df`` to ``df`` by decorating ``execute`` with the following:

.. code:: python

    from yhat import preprocess
    # ...
    # ...
    @preprocess(in_type=pd.DataFrame, out_type=pd.DataFrame)
    def execute(self, data)
    # ...
    # ...

Input
^^^^^

.. code:: js

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

Output
^^^^^^

Data will come back with columns as keys and values as lists of values.

.. code:: js

    {
      "output_column1": [ VALUE_1 ],
      "output_column2": [ VALUE_1 ]
    }

``df`` to ``dict``
~~~~~~~~~~~~~~~~~~

.. code:: python

    from yhat import preprocess
    # ...
    # ...
    @preprocess(in_type=pd.DataFrame, out_type=dict)
    def execute(self, data)
    # ...
    # ...

Input
^^^^^

.. code:: js

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

Output
^^^^^^

Selecting the ``dict`` output gives the user the ability to define their
own output format (so long as it is a valid Python dictionary.

.. code:: js

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

``dict`` to ``dict``
~~~~~~~~~~~~~~~~~~~~

This is the most "free form" means of input and output. The user can
send in any valid dictionary, process it how they like, and then return
any valid dictionary .

.. code:: python

    from yhat import preprocess
    # ...
    # ...
    @preprocess(in_type=dict, out_type=dict)
    def execute(self, data)
    # ...
    # ...

Input
^^^^^

.. code:: js

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

Output
^^^^^^

.. code:: js

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

Deploying
~~~~~~~~~

.. code:: python

    >>> yh.deploy("myExampleModel", MyExampleModel, globals())

Examples
~~~~~~~~

-  `Hello World <http://docs.yhathq.com/python/examples/hello-world>`__
-  `Hello pip <http://docs.yhathq.com/python/examples/hello-pip>`__
-  `Random
   Forest <http://docs.yhathq.com/python/examples/random-forest>`__
-  `Twitter
   Feed <http://docs.yhathq.com/python/examples/twitter-feed>`__

``yhat-cli``
------------

Usage
~~~~~

.. code:: bash

    yhat-cli config [--reset]
    yhat-cli models [--admin]
    yhat-cli model <modelname>
    yhat-cli (-h | --help)
    yhat-cli (-v | --version)

``config [--reset]``
^^^^^^^^^^^^^^^^^^^^

Configure the yhat client with your API credentials. The option
``--reset`` will reset your credentials.

``models``
^^^^^^^^^^

Return the models for your account. The option ``--admin`` returns all
models on the server, you must have admin access for this.

``model <modelname>``
^^^^^^^^^^^^^^^^^^^^^

Returns details about the given model. You must own this model to view
it.

Dependencies
------------

*Required*

-  doctopt
-  progressbar
-  pip
-  Flask
-  colorama
-  websocket-client
-  ElasticTabstops
-  dill

*Highly suggested*

-  pandas
-  sklearn

|Analytics|

.. |Analytics| image:: https://ga-beacon.appspot.com/UA-46996803-1/yhat-client/README.md
   :target: https://github.com/yhat/yhat-client
