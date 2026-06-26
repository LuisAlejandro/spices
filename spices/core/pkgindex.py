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
Linux Distribution Package Index Module.

This module fetches release metadata from upstream distribution mirrors
and builds version-to-codename index mappings used during host distribution
detection. It complements static mappings in ``spices.config.codenames`` with
live data scraped from Debian, Fedora, and Alpine release indexes.

The module contains:

1. **HTTP helpers**: Partial and full fetches of upstream release pages.
2. **Debian index builders**: Parse ``Release`` files and archived suite lists.
3. **Fedora and Alpine scrapers**: List current release directories from mirrors.
4. **Distribution index functions**: Merge live results with base codename maps
   for Debian, Fedora, Alpine, Arch, Gentoo, and CentOS.

This module enables the Spices installer to:

- Resolve codenames for current and archived Debian suites
- Discover newly published Fedora and Alpine releases automatically
- Fall back to static codename tables for rolling or fixed mappings

Usage:
    Index builders are called by ``spices.core.installer`` when assembling
    per-distribution codename tables during host detection.

Example:
    debian_codename_index()['12'] returns codename and suite labels for Debian 12.
"""

import re
from contextlib import closing
from urllib.request import Request, urlopen

import lxml.html
from packaging.version import Version

from ..config.codenames import (
    alpine_version_url,
    base_alpine_codename_index,
    base_arch_codename_index,
    base_centos_codename_index,
    base_debian_codename_index,
    base_fedora_codename_index,
    base_gentoo_codename_index,
    debian_oldversioning,
    debian_release_url_holder,
    debian_suites,
    fedora_version_url,
    olddebian_release_url_holder,
    olddebian_version_url,
)
from .logger import logger


def request_first_bytes(debian_release_url):
    """
    Fetch the first 256 bytes of a Debian release file.

    :param debian_release_url: URL of the Debian ``Release`` file.
    :return: response body as a string, or empty string on failure.
    """
    req = Request(debian_release_url)
    req.add_header("Range", "bytes={0}-{1}".format(0, 256))

    try:
        with closing(urlopen(req)) as d:
            return str(d.read())
    except Exception:
        return ""


def parse_url_html(url):
    """
    Download a URL and parse its HTML into an lxml element tree.

    :param url: URL to fetch.
    :return: parsed HTML document root element.
    """
    req = Request(url, headers={"User-Agent": "spices/0.0.3"})
    with closing(urlopen(req)) as response:
        return lxml.html.fromstring(response.read())


def get_curr_debian_codename_index(suites, url_holder):
    """
    Build a version-to-codename index from current Debian suites.

    :param suites: iterable of Debian suite names.
    :param url_holder: format string for Debian release URLs.
    :return: mapping of version strings to codename/suite lists.
    """
    logger.debug("Getting Debian versions")
    idx = {}

    for debian_suite in suites:
        debian_release_url = url_holder.format(debian_suite)

        debian_release_content = request_first_bytes(debian_release_url)

        codename = re.findall(r"Codename: (\w*)", debian_release_content)
        version = re.findall(r"Version: (\d*\.?\d*)", debian_release_content)

        if debian_suite in ["testing", "unstable"]:
            idx[debian_suite] = list(set([codename[0], debian_suite]))
            continue

        if not (codename and version):
            continue

        v = Version(version[0])
        if codename[0] in debian_oldversioning:
            version = f"{v.major}.{v.minor}"
        else:
            version = f"{v.major}"

        idx[version] = list(set([codename[0], debian_suite]))

    return idx


def get_archive_debian_codename_index():
    """
    List archived Debian suite names from the old-releases index page.

    :return: list of archived Debian version directory names.
    """
    olddebian_version_url_html = parse_url_html(olddebian_version_url)
    links = olddebian_version_url_html.cssselect("a")
    debian_versions = [
        e.get("href") for e in links if e.text_content() not in ["Name", "Last modified", "Size", "Parent Directory"]
    ]
    debian_versions = [e.strip("/") for e in debian_versions if len(e.split("-")) == 1]
    return debian_versions


def get_fedora_versions():
    """
    List Fedora release version directory names from the release archive.

    :return: list of Fedora version strings.
    """
    logger.debug("Getting Mongo versions")
    fedora_version_url_html = parse_url_html(fedora_version_url)
    links = fedora_version_url_html.cssselect("a")
    fedora_versions = [
        e.get("href")
        for e in links
        if e.text_content() not in ["Name", "Last modified", "Size", "Description", "Parent Directory", "test/"]
    ]
    fedora_versions = [e.strip("/") for e in fedora_versions if len(e.split("-")) == 1]
    return fedora_versions


def get_alpine_versions():
    """
    List Alpine Linux release version directory names from the mirror index.

    :return: list of Alpine version strings.
    """
    logger.debug("Getting Mongo versions")
    alpine_version_url_html = parse_url_html(alpine_version_url)
    links = alpine_version_url_html.cssselect("a")
    alpine_versions = [
        e.get("href") for e in links if e.text_content() not in ["latest-stable/", "MIRRORS.txt", "last-updated", "../"]
    ]
    alpine_versions = [e.strip("/") for e in alpine_versions if len(e.split("-")) == 1]
    return alpine_versions


def debian_codename_index():
    """
    Build the complete Debian version-to-codename index.

    :return: merged mapping of base, archived, and current Debian indexes.
    """
    old_debian_suites = get_archive_debian_codename_index()
    olddebians = get_curr_debian_codename_index(old_debian_suites, olddebian_release_url_holder)
    currdebians = get_curr_debian_codename_index(debian_suites, debian_release_url_holder)
    return {**base_debian_codename_index, **olddebians, **currdebians}


def fedora_codename_index():
    """
    Build the complete Fedora version-to-codename index.

    :return: merged mapping of live Fedora versions and base Fedora indexes.
    """
    fedora_versions = {f: [f] for f in get_fedora_versions()}
    return {**fedora_versions, **base_fedora_codename_index}


def alpine_codename_index():
    """
    Build the complete Alpine version-to-codename index.

    :return: merged mapping of live Alpine versions and base Alpine indexes.
    """
    alpine_versions = {f: [f] for f in get_alpine_versions()}
    return {**base_alpine_codename_index, **alpine_versions}


def arch_codename_index():
    """
    Return the Arch Linux version-to-codename index.

    :return: copy of the base Arch codename index mapping.
    """
    return {**base_arch_codename_index}


def gentoo_codename_index():
    """
    Return the Gentoo version-to-codename index.

    :return: copy of the base Gentoo codename index mapping.
    """
    return {**base_gentoo_codename_index}


def centos_codename_index():
    """
    Return the CentOS version-to-codename index.

    :return: copy of the base CentOS codename index mapping.
    """
    return {**base_centos_codename_index}
