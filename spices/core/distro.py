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

"""
Distribution install orchestration.

This module defines ``Distribution``, which binds detected host metadata to a
parsed Spices configuration and runs package manager commands for that distro.
"""

from .spices import Spices


class Distribution(object):
    """Run Spices install steps for a single detected distribution."""

    derivatives = {"ubuntu": "debian"}

    def __init__(self, distname, codename, version, data, distributions):
        """
        Initialize distribution context and build the command list.

        :param distname: detected distribution name.
        :param codename: distribution codename or release label.
        :param version: distribution version string.
        :param data: parsed spices configuration data.
        :param distributions: supported distribution metadata mapping.
        """
        self.distributions = distributions
        self.distname = distname
        self.codename = codename
        self.version = version
        self.command_config = {}
        self.distro_manager_map = {}
        self.allowed_managers = []
        self.spices = Spices(data)
        self.metadistro = self.get_metadistro()
        import pprint

        pprint.pprint(self.spices.commandlist)

    def get_metadistro(self):
        """Return the parent distribution name when ``distname`` is a derivative."""
        if self.distname in self.derivatives:
            return self.derivatives[self.distname]
        return self.distname

    def add_manager_sources(self):
        """Add repository sources for enabled managers on this distribution."""
        for cmd in self.spices.commandlist:
            enabled_distros = cmd.get_enabled_distros()
            if self.distname in enabled_distros or self.metadistro in enabled_distros:
                cmd.add_manager_sources()

    def add_trusted_keys(self):
        """Install trusted keys for enabled managers on this distribution."""
        for cmd in self.spices.commandlist:
            enabled_distros = cmd.get_enabled_distros()
            if self.distname in enabled_distros or self.metadistro in enabled_distros:
                cmd.add_trusted_keys()

    def update_package_db(self):
        """Refresh package indexes for enabled managers on this distribution."""
        for cmd in self.spices.commandlist:
            enabled_distros = cmd.get_enabled_distros()
            if self.distname in enabled_distros or self.metadistro in enabled_distros:
                cmd.update()

    def install(self):
        """Install dependencies for enabled managers on this distribution."""
        for cmd in self.spices.commandlist:
            enabled_distros = cmd.get_enabled_distros()
            if self.distname in enabled_distros or self.metadistro in enabled_distros:
                cmd.install()
