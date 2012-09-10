#!/bin/bash
## begin license ##
# 
# All rights reserved.
# 
# Copyright (C) 2012 Seecr (Seek You Too B.V.) http://seecr.nl
# 
## end license ##

set -e

rm -rf tmp build
pycmd=python2.6

$pycmd setup.py install --root tmp --install-scripts=usr/bin 

export PYTHONPATH=`pwd`/tmp/usr/local/lib/python2.6/dist-packages

cp -r test tmp/test
cp seecr/__init__.py $PYTHONPATH/seecr/

(
cd tmp/test
./alltests.sh
)

rm -rf tmp build
