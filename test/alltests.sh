#!/bin/bash
## begin license ##
# 
# All rights reserved.
# 
# Copyright (C) 2011-2012 Seecr (Seek You Too B.V.) http://seecr.nl
# 
## end license ##

set -o errexit
export LANG=en_US.UTF-8
export PYTHONPATH=.:"$PYTHONPATH"
python2.6 _alltests.py "$@"
