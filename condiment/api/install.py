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

import os
import yaml

from condiment.core.installer import Installer


def main(**kwargs):

    currdir = os.getcwd()
    condimentpath = os.path.join(currdir, '.condiment.yml')

    if not os.path.isfile(condimentpath):
        print('')
        return 1

    with open(condimentpath) as c:
        installer = Installer(yaml.safe_load(c.read()))
        installer.get_distro_data()
        installer.normalize_distro_data()
        installer.check_binaries()
