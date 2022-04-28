# -*- coding: utf-8 -*-
#
# Please refer to AUTHORS.rst for a complete list of Copyright holders.
# Copyright (C) 2016-2022, Condiment Developers.

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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
