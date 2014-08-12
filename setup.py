#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 Luis Alejandro Martínez Faneyth
#
# This file is part of Condiment.
#
# Condiment is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Condiment is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

This script invokes the setuptools script for Condiment.

For more information about this file, see documentation on
``condiment/common/setup/utils.py``

"""

from setuptools import setup

from condiment import BASEDIR
from condiment.common.setup.utils import get_setup_data

setup(**get_setup_data(BASEDIR))
