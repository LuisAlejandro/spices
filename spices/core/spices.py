# -*- coding: utf-8 -*-
#
# Please refer to AUTHORS.rst for a complete list of Copyright holders.
# Copyright (C) 2016-2022, Spices Developers.

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

from .errors import SpicesAreEmpty, ThereAreNoCommands
from .managers import Apk, Apt, Bundler, Npm, Pacman, Pip, Portage, Script, Yarn, Yum


class Spices(object):

    native_managers_map = {
        'apt-get': Apt,
        'apt': Apt,
        'yum': Yum,
        'apk': Apk,
        'pacman': Pacman,
        'emerge': Portage,
        'portage': Portage,
        'custom': Script
    }

    distribution_map = {
        'debian': Apt,
        'fedora': Yum,
        'alpine': Apk,
        'arch': Pacman,
        'gentoo': Portage,
        'centos': Yum
    }

    other_managers_map = {
        'npm': Npm,
        'yarn': Yarn,
        'pip': Pip,
        'bundler': Bundler,
    }

    def __init__(self, content):
        eqmap = {
            **self.native_managers_map,
            **self.distribution_map,
            **self.other_managers_map,
        }
        allowed_managers = eqmap.keys()

        self.__eqmap = eqmap
        self.__allowed_managers = allowed_managers

        if not content:
            raise SpicesAreEmpty()

        # Merge the content incrementally if it's a list
        if isinstance(content, list):
            self.content = self.merge_data_incrementally(content)
        else:
            self.content = content

        self.commandlist = []
        self.generate_commandlist()

        if not self.commandlist:
            raise ThereAreNoCommands()

    def merge_data_incrementally(self, content_list):
        """
        Merges data incrementally from a list of tuples.
        Each tuple contains (config_dict, file_path).
        Merges from last to first: third merges into second, second into first, etc.
        """
        if not content_list:
            return {}

        if len(content_list) == 1:
            return content_list[0][0].copy() if content_list[0][0] else {}

        # Start from the end and work backwards
        # For [A, B, C]: C merges into B, then B merges into A
        result_data = content_list[-1][0].copy() if content_list[-1][0] else {}

        # Merge from second-to-last down to first
        for i in range(len(content_list) - 2, -1, -1):
            item_data = content_list[i][0]
            if item_data:
                result_data = self._deep_merge_dicts(item_data, result_data)

        return result_data

    def _deep_merge_dicts(self, dict1, dict2):
        """
        Deep merge two dictionaries. dict2 values take precedence over dict1.
        """
        result = dict1.copy()

        for key, value in dict2.items():
            if key in result:
                if isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = self._deep_merge_dicts(result[key], value)
                elif isinstance(result[key], list) and isinstance(value, list):
                    # For lists, extend them
                    result[key] = result[key] + value
                else:
                    # For other types, dict2 value takes precedence
                    result[key] = value
            else:
                result[key] = value

        return result

    def generate_commandlist(self):
        for manager, data in self.content['managers'].items():
            if manager not in self.__allowed_managers:
                continue
            if 'dependencies' in data:
                Manager = self.__eqmap[manager]
                d = manager if manager in self.distribution_map else None
                self.commandlist.append(Manager(data['dependencies'], d, data))
            if 'postinstall' in data:
                self.commandlist.append(Script(data['postinstall']))
