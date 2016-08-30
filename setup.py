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
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ),
    install_requires=[
        "pip",
        "Flask==0.10.1",
        "websocket-client==0.12.0",
        "dill==0.2b1",
        "terragon==0.2.0",
        "progressbar==2.2",
        "poster==0.8.1"
    ],
    long_description=open("README.rst").read(),
    keywords=['yhat', 'scikits', 'numpy', 'pandas'],
)
