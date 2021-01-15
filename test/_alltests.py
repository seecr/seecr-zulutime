#!/usr/bin/python
# -*- coding: utf-8 -*-
## begin license ##
#
# Zulutime helps formatting and parsing timestamps.
#
# Copyright (C) 2012, 2014, 2020-2021 Seecr (Seek You Too B.V.) https://seecr.nl
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

from sys import path
from os import system, listdir
from os.path import isdir, join
system("find .. -name '*.pyc' | xargs rm -f")
if isdir('../deps.d'):
    for d in listdir('../deps.d'):
        path.insert(0, join('../deps.d', d))
path.insert(0, '..')

import unittest

from zulutimetest import ZuluTimeTest

if __name__ == '__main__':
    unittest.main()
