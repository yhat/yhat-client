from distutils.core import setup
from setuptools import find_packages

setup(
        name="yhat",
        version="0.6.0",
        author="Greg Lamp",
        author_email="greg@yhathq.com",
        url="https://github.com/yhat/yhat-client",
        packages=find_packages(),
        description="plotting in the terminal",
        install_requires=[],
        scripts=['bin/yhat-cli']
)
