#!/bin/bash

pandoc -f markdown -t rst README.md > README.rst
python setup.py install
v1=`pip freeze | grep "yhat=="`
v2=`python -c "import yhat; print yhat.__version__"`
if [[ "${v1}"!="${v2}" ]]; then
fi
python setup.py install sdist $1

