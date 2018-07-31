#!/bin/bash
## begin license ##
#
# Zulutime helps formatting and parsing timestamps.
#
# Copyright (C) 2012, 2014 Seecr (Seek You Too B.V.) http://seecr.nl
#
# This file is part of "Zulutime"
#
# "Zulutime" is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# "Zulutime" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with "Zulutime"; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

set -e

rm -rf tmp build
pycmd=python2.7

$pycmd setup.py install --root tmp --install-scripts=usr/bin 

export PYTHONPATH=`pwd`/tmp/usr/local/lib/python2.7/dist-packages

cp -r test tmp/test
cp seecr/__init__.py $PYTHONPATH/seecr/

(
cd tmp/test
./alltests.sh
)

rm -rf tmp build
