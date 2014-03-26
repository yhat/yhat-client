#!/bin/bash

cd /Users/glamp/repos/yhat/clients/python-client/
python setup.py install > /dev/null
cd /Users/glamp/repos/yhat/clients/python-client/tests/xin/src
python stickytext-yhat.py
echo "---"
/Users/glamp/repos/yhat/enterprise/yhat/scripts/decompress.py StickyText.yhat | jq .modules[].name
echo "---"
