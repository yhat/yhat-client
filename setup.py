from setuptools import setup, find_packages

required = ['requests==0.14.2']

setup(
    author='glamp',
    name='yhat',
    version='0.1.9',
    description='Official Python driver for the yhat api',
    #long_description=open('README.txt').read(),
    url='https://github.com/yhat/yhat-client',
    license='Apache License',
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ),
    keywords=['yhat', 'scikits', 'numpy', 'pandas'],
    packages=find_packages(),
    install_requires=required
)
