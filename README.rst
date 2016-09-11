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

|Analytics|

.. |Analytics| image:: https://ga-beacon.appspot.com/UA-46996803-1/yhat-client/README.md
   :target: https://github.com/yhat/yhat-client
