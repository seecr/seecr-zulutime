#!/usr/bin/env python
## begin license ##
# 
# All rights reserved.
# 
# Copyright (C) 2012 Seecr (Seek You Too B.V.) http://seecr.nl
# 
## end license ##

from distutils.core import setup

setup(
    name='seecr-zulutime',
    version='%VERSION%',
    packages=[
        'seecr.zulutime', 
    ],
    url='http://seecr.nl',
    author='Seecr',
    author_email='info@seecr.nl',
    description="Zulutime helps formatting and parsing timestamps.",
    long_description="Zulutime helps formatting and parsing timestamps.",
    platforms=['linux'],
)

