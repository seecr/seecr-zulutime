#!/bin/bash
## begin license ##
#
# Zulutime helps formatting and parsing timestamps.
#
# Copyright (C) 2011-2012, 2014, 2020-2021 Seecr (Seek You Too B.V.) https://seecr.nl
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

set -o errexit
export LANG=en_US.UTF-8
export PYTHONPATH=.:"$PYTHONPATH"
export PYTHONWARNINGS=default

python3 _alltests.py "$@"
