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
Linux Distribution Installer Module.

This module provides the ``Installer`` class for detecting the host Linux
distribution and orchestrating Spices dependency installation. It serves as the
main entry point for resolving distribution identity and driving package manager
operations defined in a ``.spices.yml`` configuration.

The installer:

1. **Builds codename indexes** from live package index data for supported
   distributions (Debian, Arch, Fedora, Alpine, CentOS, Gentoo).
2. **Detects the host distribution** using multiple strategies: ``lsb_release``,
   distribution-specific release files, ``/etc/os-release``, dpkg origins, and
   APT policy output.
3. **Normalizes** detected codename and version values against the Spices
   distribution database and validates support.
4. **Executes installation** by delegating to a ``Distribution`` instance for
   trusted keys, repository sources, package database updates, and installs.

Raises ``CannotIdentifyDistribution`` when detection fails and
``UnsupportedDistribution`` when the host is not supported.
"""

import os
import re
from distutils.spawn import find_executable
from subprocess import PIPE, Popen  # nosec B404
from typing import Any

from dotenv import dotenv_values
from packaging.version import Version

from ..config.distributions import distrodata
from .distro import Distribution
from .errors import CannotIdentifyDistribution, UnsupportedDistribution
from .logger import logger
from .pkgindex import (
    alpine_codename_index,
    arch_codename_index,
    centos_codename_index,
    debian_codename_index,
    fedora_codename_index,
    gentoo_codename_index,
)
from .utils import flatten_list


class Installer(object):
    """
    Detect the host Linux distribution and install Spices dependencies.

    The installer probes release files and commands, normalizes codename and
    version data against the Spices distribution database, and runs the full
    install workflow through a ``Distribution`` object.
    """

    def __init__(self, spices):
        """
        Initialize the installer and detect the host distribution.

        :param spices: validated Spices configuration from ``.spices.yml``.
        """
        self.distname: str = ""
        self.codename: str = ""
        self.version: str = ""
        self.metadistname = ""
        self.metacodename = ""
        self.apt_policy_data = []
        self.lsb_release_command = find_executable("lsb_release")
        self.os_release = "/etc/os-release"
        self.lsb_release = "/etc/lsb-release"
        self.dpkg_origins = "/etc/dpkg/origins/default"
        self.debian_release = "/etc/debian_version"
        self.fedora_release = "/etc/fedora-release"
        self.alpine_release = "/etc/alpine-release"
        self.arch_release = "/etc/arch-release"
        self.gentoo_release = "/etc/gentoo-release"
        self.centos_release = "/etc/centos-release"
        self.env = os.environ.copy()
        self.env["LC_ALL"] = "C"

        self.longnames = {"v": "version", "o": "origin", "a": "suite", "c": "component", "l": "label"}

        self.spicesdata = spices
        self.distributions: dict[str, Any] = distrodata
        self.codenames: dict[str, Any] = {}
        self.revcodenames: dict[str, str] = {}

        self.populate_codename_index()
        self.get_distro_data()
        self.normalize_distro_data()

    def populate_codename_index(self):
        """Populate codename mappings from the package index."""
        logger.info("Generating distributions database")
        self.distributions["debian"]["codenames"] = debian_codename_index()
        self.distributions["arch"]["codenames"] = arch_codename_index()
        self.distributions["fedora"]["codenames"] = fedora_codename_index()
        self.distributions["alpine"]["codenames"] = alpine_codename_index()
        self.distributions["centos"]["codenames"] = centos_codename_index()
        self.distributions["gentoo"]["codenames"] = gentoo_codename_index()

    def codename_index(self, x):
        """
        Return a sort key for an APT policy release tuple.

        :param x: a ``(priority, release_dict)`` tuple from apt policy output.
        :return: an integer rank, suite string, or ``0`` if suite is missing.
        """
        suite = x[1].get("suite")
        order = list(self.distributions[self.distname]["codenames"].items())
        order.sort()
        order = list(flatten_list(list(zip(*order))[1]))

        if suite:
            if suite in order:
                return int(len(order) - order.index(suite))
            else:
                return suite
        return 0

    def parse_apt_policy(self):
        """
        Parse ``apt-cache policy`` output into release records.

        :return: a list of ``(priority, release_dict)`` tuples stored on the
            installer instance.
        """
        retval = {}
        policy = (
            Popen(args=["apt-cache", "policy"], stdout=PIPE, stderr=PIPE, env=self.env, close_fds=True)  # nosec B603
            .communicate()[0]
            .decode("utf-8")
        )

        for line in policy.split("\n"):
            line = line.strip()
            m = re.match(r"(-?\d+)", line)

            if m:
                priority = int(m.group(1))

            if line.startswith("release"):
                bits = line.split(" ", 1)

                if len(bits) > 1:
                    for bit in bits[1].split(","):
                        kv = bit.split("=", 1)

                        if len(kv) > 1:
                            k, v = kv[:2]

                            if k in self.longnames:
                                retval[self.longnames[k]] = v

                    self.apt_policy_data.append((priority, retval))
        return self.apt_policy_data

    def get_codename_from_apt(self, origin, component="main"):
        """
        Resolve the highest-priority suite codename from APT policy.

        :param origin: the APT origin identifier (for example ``Debian``).
        :param component: the APT component to match (default ``main``).
        :return: the suite codename string for the selected release.
        """
        releases = self.parse_apt_policy()
        releases = [
            x
            for x in releases
            if (
                x[1].get("origin", "").lower() == origin
                and x[1].get("component", "").lower() == component
                and x[1].get("label", "").lower() == origin
            )
        ]

        releases.sort(key=lambda tuple: tuple[0], reverse=True)

        max_priority = releases[0][0]
        releases = [x for x in releases if x[0] == max_priority]
        releases.sort(key=self.codename_index)

        return releases[0][1]["suite"]

    def parse_os_release(self, release):
        """
        Parse a dotenv-style OS release file.

        :param release: path to an ``os-release`` or ``lsb-release`` file.
        :return: a mapping of key/value pairs from the file.
        """
        return dotenv_values(release)

    def cat_file(self, release):
        """
        Read and return the full contents of a release file.

        :param release: path to the file to read.
        :return: the file contents as a string.
        """
        with open(release) as content:
            return content.read()

    def parse_dpkg_origins(self, origins):
        """
        Parse a dpkg origins file into key/value pairs.

        :param origins: path to the dpkg origins file.
        :return: a mapping of field names to values.
        """
        dpkg_origins_data = {}
        with open(origins) as content:
            contentlist = content.read()
        for j in contentlist.split("\n"):
            keyvalue = j.split(":")
            if len(keyvalue) > 1:
                dpkg_origins_data[keyvalue[0].strip()] = keyvalue[1].strip()
        return dpkg_origins_data

    def cmd_return_full(self, args, env):
        """
        Run a subprocess and return its full stdout.

        :param args: command argument list passed to ``Popen``.
        :param env: environment mapping for the subprocess.
        :return: decoded stdout from the command.
        """
        return Popen(args=args, stdout=PIPE, stderr=PIPE, env=env, close_fds=True).communicate()[0].decode("utf-8")  # nosec B603

    def cmd_return_first_line(self, args, env) -> str:
        """
        Run a subprocess and return the first line of stdout.

        :param args: command argument list passed to ``Popen``.
        :param env: environment mapping for the subprocess.
        :return: the first line of decoded stdout.
        """
        return (
            (
                Popen(args=args, stdout=PIPE, stderr=PIPE, env=env, close_fds=True)  # nosec B603
                .communicate()[0]
                .decode("utf-8")
                .split("\n")[0]
            )
            or ""
        )

    def try_lsb_release_command(self):
        """Detect distribution data using the ``lsb_release`` command."""
        if (not self.distname) and self.lsb_release_command:
            self.distname = self.cmd_return_first_line([self.lsb_release_command, "-is"], self.env)
            self.codename = self.cmd_return_first_line([self.lsb_release_command, "-cs"], self.env)
            self.version = self.cmd_return_first_line([self.lsb_release_command, "-rs"], self.env)

    def try_arch_release_file(self):
        """Detect Arch Linux from ``/etc/arch-release``."""
        if (not self.distname) and os.path.exists(self.arch_release):
            self.distname = "arch"
            self.codename = "rolling"
            self.version = "rolling"

    def try_gentoo_release_file(self):
        """Detect Gentoo from ``/etc/gentoo-release``."""
        if (not self.distname) and os.path.exists(self.gentoo_release):
            self.distname = "gentoo"
            self.codename = "rolling"
            self.version = "rolling"

    def try_fedora_release_file(self):
        """Detect Fedora from ``/etc/fedora-release``."""
        if (not self.distname) and os.path.exists(self.fedora_release):
            relstr = self.cat_file(self.fedora_release)
            relarray = relstr.split()
            version = Version(relarray[2])
            self.distname = relarray[0]
            self.version = f"{version.major}"
            codename = re.match(r"^.*\((.*)\)$", relstr)
            if codename:
                self.codename = codename.groups()[0]

    def try_alpine_release_file(self):
        """Detect Alpine Linux from ``/etc/alpine-release``."""
        if (not self.distname) and os.path.exists(self.alpine_release):
            relstr = self.cat_file(self.alpine_release)
            relarray = relstr.split()
            version = Version(relarray[2])
            self.distname = relarray[0]
            self.version = f"{version.major}"
            codename = re.match(r"^.*\((.*)\)$", relstr)
            if codename:
                self.codename = codename.groups()[0]

    def try_centos_release_file(self):
        """Detect CentOS from ``/etc/centos-release``."""
        if (not self.distname) and os.path.exists(self.centos_release):
            relstr = self.cat_file(self.centos_release)
            relarray = relstr.split()
            stream = "stream" if relarray[1].lower() == "stream" else ""
            version = Version(relarray[3])
            self.distname = relarray[0]
            self.codename = f"{stream}{version.major}"

    def try_lsb_release_file(self):
        """Detect distribution data from ``/etc/lsb-release``."""
        if (not self.distname) and os.path.exists(self.lsb_release):
            rel = self.parse_os_release(self.lsb_release)
            self.distname = rel.get("DISTRIB_ID") or ""
            self.codename = rel.get("DISTRIB_CODENAME") or ""
            self.version = rel.get("DISTRIB_RELEASE") or ""

    def try_os_release_file(self):
        """Detect distribution data from ``/etc/os-release``."""
        if (not self.distname) and os.path.exists(self.os_release):
            rel = self.parse_os_release(self.os_release)
            self.distname = rel.get("ID") or ""
            self.codename = rel.get("VERSION_CODENAME") or ""
            self.version = rel.get("VERSION_ID") or ""

    def try_dpkg_origins(self):
        """Detect Debian vendor from ``/etc/dpkg/origins/default``."""
        if (not self.distname) and os.path.exists(self.dpkg_origins):
            origins = self.parse_dpkg_origins(self.dpkg_origins)
            self.distname = origins.get("VENDOR") or ""

    def try_apt(self):
        """Resolve Debian codename from APT policy or ``/etc/debian_version``."""
        if self.distname and (not self.codename) and os.path.exists(self.debian_release):
            rel = self.cat_file(self.debian_release)

            if re.findall(r".*/.*", rel):
                self.codename = self.get_codename_from_apt(self.distname)
            else:
                self.codename = rel

    def get_distro_data(self):
        """
        Detect distribution name, codename, and version.

        Runs all detection strategies in order and builds reverse codename
        mappings. Raises ``CannotIdentifyDistribution`` when detection fails.
        """
        logger.info("Attempting to identify your distribution")

        self.try_lsb_release_command()
        self.try_arch_release_file()
        self.try_gentoo_release_file()
        self.try_fedora_release_file()
        self.try_centos_release_file()
        self.try_lsb_release_file()
        self.try_os_release_file()
        self.try_dpkg_origins()
        self.try_apt()

        if not (self.distname and self.codename):
            raise CannotIdentifyDistribution()

        self.codenames = self.distributions[self.distname]["codenames"]

        for k, v in self.codenames.items():
            if len(v) > 1:
                for j in v:
                    self.revcodenames[j] = k
            else:
                self.revcodenames[v[0]] = k

    def normalize_distro_data(self):
        """
        Normalize codename and version and create the Distribution object.

        Maps between version numbers and codenames, validates support, and
        raises ``UnsupportedDistribution`` when the host is not supported.
        """
        regex = re.compile(r"^(\d+)\.(\d+)(\.(\d+))?([ab](\d+))?$", re.VERBOSE)
        codematch = regex.match(self.codename or "")

        if not codematch:
            self.version = self.revcodenames[self.codename]
        else:
            (major, minor, patch, pre, prenum) = codematch.group(1, 2, 4, 5, 6)
            self.version = ".".join(list(filter(None, [major, minor, patch, pre, prenum])))
        vermatch = regex.match(self.version or "")
        if vermatch:
            self.codename = self.codenames[str(float(vermatch.group(1)))][0]
        else:
            self.codename = self.codenames[str(self.version)][0]

        if self.is_supported_codename():
            logger.info("You are using %s (%s)." % (self.distname, self.codename))
            self.distribution = Distribution(
                self.distname, self.codename, self.version, self.spicesdata, self.distributions
            )
        else:
            raise UnsupportedDistribution()

    def is_supported_distname(self):
        """
        Check whether the detected distribution name is known to Spices.

        :return: ``True`` if ``distname`` is in the distributions database.
        """
        if self.distname in self.distributions:
            return True
        return False

    def is_supported_codename(self):
        """
        Check whether the detected codename is supported for this distribution.

        :return: ``True`` if the codename is valid for the current version.
        """
        if self.is_supported_distname():
            if self.codename in self.distributions[self.distname]["codenames"][self.version]:
                return True
        return False

    def execute(self):
        """Run the full installation workflow."""
        logger.info("Installing missing dependencies ...")
        self.add_trusted_keys()
        self.add_manager_sources()
        self.update_package_db()
        self.install()

    def add_trusted_keys(self):
        """Add trusted GPG keys via the distribution package managers."""
        self.distribution.add_trusted_keys()

    def add_manager_sources(self):
        """Add package manager repository sources."""
        self.distribution.add_manager_sources()

    def update_package_db(self):
        """Update package manager databases."""
        self.distribution.update_package_db()

    def install(self):
        """Install dependencies via the distribution package managers."""
        self.distribution.install()
