# -*- coding: utf-8 -*-
#
#   This file is part of Condiment.
#   Copyright (C) 2020-2022, Condiment Developers.
#
#   Please refer to AUTHORS.rst for a complete list of Copyright holders.
#
#   Condiment is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   Condiment is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program. If not, see http://www.gnu.org/licenses.

from __future__ import with_statement, print_function

from distutils.spawn import find_executable

from .logger import logger


class Distribution(object):

    def __init__(self, distname, codename, containers, distributions):
        self.distributions = distributions
        self.distname = distname
        self.codename = codename
        self.containers = containers

    def get_binaries(self):
        binaries = []
        for dep in self.get_dependencies():
            if dep.get('containers') == self.containers \
               and dep.get('binaries'):
                binaries.extend(dep.get('binaries'))
        return binaries

    def get_managers(self):
        return self.distributions[self.distname]['managers']

    def get_dependencies(self):
        return self.distributions[self.distname]['dependencies'][self.codename]

    def check_binaries(self):
        logger.info('Checking for dependencies ...')
        for b in self.get_binaries():
            if not find_executable(b):
                logger.info('%s not found!' % b)
                return False
        logger.info('Everything ok!')
        return True
