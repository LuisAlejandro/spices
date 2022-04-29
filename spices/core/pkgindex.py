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

import re
from contextlib import closing
from urllib.request import urlopen, Request

import lxml.html

from .logger import logger

archlinux_versions = ['rolling']

alpine_version_url = 'https://dl-cdn.alpinelinux.org/alpine'
ubuntu_version_url = 'http://archive.ubuntu.com/ubuntu/dists'
fedora_version_url = 'https://dl.fedoraproject.org/pub/archive/fedora/linux/releases'

debian_release_url_holder = 'http://deb.debian.org/debian/dists/{0}/Release'
debian_suites = ['oldoldstable', 'oldstable', 'stable', 'testing', 'unstable']


def get_debian_versions():
    logger.debug('Getting Debian versions')
    debian_versions = []

    for debian_suite in debian_suites:
        debian_release_url = debian_release_url_holder.format(debian_suite)

        r = Request(debian_release_url)
        r.add_header('Range', 'bytes={0}-{1}'.format(0, 256))

        with closing(urlopen(r)) as d:
            debian_release_content = d.read()

        debian_versions.append(re.findall('Codename: (.*)',
                                          debian_release_content)[0])

    return debian_versions


def get_ubuntu_versions():
    logger.debug('Getting Mongo versions')

    ubuntu_version_url_html = lxml.html.parse(ubuntu_version_url).getroot()
    links = ubuntu_version_url_html.cssselect('a')
    ubuntu_versions = [e.get('href') for e in links]
    ubuntu_versions = [e for e in ubuntu_versions if len(e.split('-')) == 1]
    ubuntu_versions.remove('devel')
    return ubuntu_versions


def get_fedora_versions():
    logger.debug('Getting Mongo versions')

    fedora_version_url_html = lxml.html.parse(fedora_version_url).getroot()
    links = fedora_version_url_html.cssselect('a')
    fedora_versions = [e.get('href') for e in links]
    fedora_versions = [e for e in fedora_versions if len(e.split('-')) == 1]
    fedora_versions.remove('devel')
    return fedora_versions


def get_alpine_versions():
    logger.debug('Getting Mongo versions')

    alpine_version_url_html = lxml.html.parse(alpine_version_url).getroot()
    links = alpine_version_url_html.cssselect('a')
    alpine_versions = [e.get('href') for e in links]

    return [e for e in alpine_versions if e.startswith('v')] + ['edge']
