from setuptools import setup, find_packages

required = ['requests==0.14.2']

setup(
    author='glamp',
    name='skdeploy-api',
    version='0.0.1',
    description='Official Python driver for the skdeploy api',
    long_description=open('README.md').read(),
    url='https://github.com/anecdotally/skdeploy-client/',
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
    keywords=['skdeploy', 'scikits', 'numpy', 'pandas'],
    packages=find_packages(),
    install_requires=required
)