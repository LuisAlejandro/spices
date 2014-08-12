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

condiment.config.pkg
=================


"""
from condiment import BASEDIR
from condiment.config.base import CONFDIR, DOCDIR
from condiment.common.utils import get_path, cat_file, readconfig
from condiment.common.setup.utils import (get_requirements, get_dependency_links,
                                       get_classifiers)

platforms = ('Any')
keywords = ('Social Network',
            'Continuous Integration',
            'Source Code Management')
f_readme = get_path([DOCDIR, 'rst', 'readme.rst'])
f_python_classifiers = get_path([CONFDIR, 'data', 'python-classifiers.list'])
f_exclude_sources = get_path([CONFDIR, 'data', 'exclude-sources.list'])
f_exclude_packages = get_path([CONFDIR, 'data', 'exclude-packages.list'])
f_exclude_patterns = get_path([CONFDIR, 'data', 'exclude-patterns.list'])
f_include_data_patterns = get_path([CONFDIR, 'data',
                                    'include-data-patterns.list'])

f_python_dependencies = get_path([CONFDIR, 'data', 'python-dependencies.list'])
f_debian_run_dependencies = get_path([CONFDIR, 'data',
                                      'debian-run-dependencies.list'])
f_debian_build_dependencies = get_path([CONFDIR, 'data',
                                        'debian-build-dependencies.list'])

exclude_sources = readconfig(filename=f_exclude_sources, conffile=False)
exclude_packages = readconfig(filename=f_exclude_packages, conffile=False)
exclude_patterns = readconfig(filename=f_exclude_patterns, conffile=False)
include_data_patterns = readconfig(filename=f_include_data_patterns,
                                   conffile=False)

long_description = cat_file(filename=f_readme)
classifiers = get_classifiers(filename=f_python_classifiers)
install_requires = get_requirements(filename=f_python_dependencies)
dependency_links = get_dependency_links(filename=f_python_dependencies)

python_dependencies = readconfig(filename=f_python_dependencies,
                                 conffile=False, strip_comments=False)
debian_run_dependencies = readconfig(filename=f_debian_run_dependencies,
                                     conffile=False)
debian_build_dependencies = readconfig(filename=f_debian_build_dependencies,
                                       conffile=False)

debian_base_image_script = get_path([BASEDIR, 'condiment', 'data', 'scripts',
                                     'debian-base-image.sh'])
condiment_base_image_script = get_path([BASEDIR, 'condiment', 'data', 'scripts',
                                     'condiment-base-image.sh'])
condiment_django_syncdb_script = get_path([BASEDIR, 'condiment', 'data', 'scripts',
                                        'django-syncdb.sh'])
condiment_django_runserver_script = get_path([BASEDIR, 'condiment', 'data', 'scripts',
                                           'django-runserver.sh'])
condiment_start_container_script = get_path([BASEDIR, 'condiment', 'data', 'scripts',
                                          'start-container.sh'])
veeweedir = get_path([BASEDIR, 'condiment', 'data', 'scripts', 'veewee'])
