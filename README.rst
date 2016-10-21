Yhat Python Client
==================

This is the connection to the Yhat API. If you'd like to read more,
`visit our
docs <http://docs.yhat.com/knowledge-base/docs/scienceops/user-guide/model-building/python-client.html>`__.

**Table of Contents:**

-  `Installation <#installation>`__
-  `Quickstart <#quickstart>`__

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

|Analytics|

.. |Analytics| image:: https://ga-beacon.appspot.com/UA-46996803-1/yhat-client/README.md
   :target: https://github.com/yhat/yhat-client
