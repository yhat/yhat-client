from distutils.core import setup
from setuptools import find_packages

setup(
    name="yhat",
    version="1.3.8",
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
        "terragon==0.1.4",
        "progressbar==2.2",
        "poster==0.8.1"
    ],
    long_description=open("README.rst").read(),
    keywords=['yhat', 'scikits', 'numpy', 'pandas'],
)
