#!/usr/bin/env python
try:
    from setuptools import setup
except (ImportError, err):
    from distutils.core import setup

from ahem import VERSION

setup(
    name='Ahem',
    version='.'.join(map(str,VERSION)),
    description='Simple, but rich, declarative notification framework for Django',
    packages=['ahem'],
    include_package_data=True,
    license='BSD',
    author='Loren Davie',
    author_email='code@axilent.com',
    url='https://github.com/Axilent/Ahem',
    install_requires=['Django>=1.4'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
