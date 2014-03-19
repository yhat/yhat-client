#!/bin/bash

cd /Users/glamp/repos/yhat/clients/python-client/
python setup.py install > /dev/null
cd /Users/glamp/repos/yhat/clients/python-client/tests/twitter
python twitterRanker.py
echo "---"
/Users/glamp/repos/yhat/enterprise/yhat/scripts/decompress.py Example.yhat | jq --raw-output .code
/Users/glamp/repos/yhat/enterprise/yhat/scripts/decompress.py Example.yhat | jq --raw-output .
rm Example.yhat
echo "---"
