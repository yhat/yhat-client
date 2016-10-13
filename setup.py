import os

from distutils.core import setup
from setuptools import find_packages

# Get version from defined python file
with open(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'yhat',
        'version.py'
    )
) as fh:
    version = fh.read().strip()
exec(version)

setup(
    name="yhat",
    version=__version__,
    author="Greg Lamp",
    author_email="greg@yhathq.com",
    url="https://github.com/yhat/yhat-client",
    packages=find_packages(),
    description="Python client for Yhat (http://yhathq.com/)",
    license="BSD",
    classifiers=(
    ),
    install_requires=[
        "pip",
        "Flask==0.10.1",
        "websocket-client==0.12.0",
        "dill==0.2b1",
        "terragon==0.2.3",
        "progressbar==2.2",
        "poster==0.8.1",
        "simplejson==3.8.2"
    ],
    long_description=open("README.rst").read(),
    keywords=['yhat', 'scikits', 'numpy', 'pandas'],
)
