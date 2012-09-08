#!/usr/bin/python
# -*- coding: utf-8 -*-

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
