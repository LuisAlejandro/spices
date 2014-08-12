#!/usr/bin/make -f
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


# COMMON VARIABLES & CONFIG ----------------------------------------------------

SHELL = sh -e
PATH = "/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
FAB = $(shell which fab)
BASH = $(shell which bash)
SU = $(shell which su)
SUDO = $(shell which sudo)
APTITUDE = $(shell which aptitude)
USER = $(shell id -u -n)
ROOT = root


# HELPER TASKS -----------------------------------------------------------------

dependencies:

	@# With this script we will satisfy dependencies on the supported
	@# distributions.
	@$(SUDO) PYTHONPATH=$(BASEDIR) $(PYTHON) condiment/common/dependencies.py

generate_debian_base_image_i386: dependencies

	@$(FAB) generate_debian_base_image_i386

generate_debian_base_image_amd64: dependencies

	@$(FAB) generate_debian_base_image_amd64

generate_condiment_base_image_i386: dependencies

	@$(FAB) generate_condiment_base_image_i386

generate_condiment_base_image_amd64: dependencies

	@$(FAB) generate_condiment_base_image_amd64

kill_all_containers: dependencies

	@$(FAB) kill_all_containers

kill_all_images: dependencies

	@$(FAB) kill_all_images

kill_condiment_images: dependencies

	@$(FAB) kill_condiment_images


# COMMON TASKS -----------------------------------------------------------------

environment: dependencies

	@$(FAB) environment
	@$(FAB) django:command='syncdb'

start: dependencies

	@$(FAB) django:command='runserver'

stop: dependencies

	@$(FAB) stop

login: dependencies

	@$(FAB) login

reset: dependencies

	@$(FAB) reset

update: dependencies

	@$(FAB) update

sync: dependencies

	@$(FAB) django:command='syncdb'

shell: dependencies

	@$(FAB) django:command='shell'

update_catalog: dependencies

	@$(FAB) setuptools:command='update_catalog'

compile_catalog: dependencies

	@$(FAB) setuptools:command='compile_catalog'

init_catalog: dependencies

	@$(FAB) setuptools:command='init_catalog'

extract_messages: dependencies

	@$(FAB) setuptools:command='extract_messages'

tx_push: dependencies

	@$(FAB) tx:command='push'

tx_pull: dependencies

	@$(FAB) tx:command='pull'

build: dependencies

	@$(FAB) setuptools:command='build'

build_sphinx: dependencies

	@$(FAB) setuptools:command='build_sphinx'

build_mo: dependencies

	@$(FAB) setuptools:command='build_mo'

build_css: dependencies

	@$(FAB) setuptools:command='build_css'

build_js: dependencies

	@$(FAB) setuptools:command='build_js'

build_man: dependencies

	@$(FAB) setuptools:command='build_man'

clean: dependencies

	@$(FAB) setuptools:command='clean'

clean_css: dependencies

	@$(FAB) setuptools:command='clean_css'

clean_js: dependencies

	@$(FAB) setuptools:command='clean_js'

clean_mo: dependencies

	@$(FAB) setuptools:command='clean_mo'

clean_sphinx: dependencies

	@$(FAB) setuptools:command='clean_sphinx'

clean_man: dependencies

	@$(FAB) setuptools:command='clean_man'

clean_dist: dependencies

	@$(FAB) setuptools:command='clean_dist'

clean_pyc: dependencies

	@$(FAB) setuptools:command='clean_pyc'

test: dependencies

	@$(FAB) setuptools:command='test'

install: dependencies

	@$(FAB) setuptools:command='install'

bdist: dependencies

	@$(FAB) setuptools:command='bdist'

sdist: dependencies

	@$(FAB) setuptools:command='sdist'

report_setup_data: dependencies

	@$(FAB) setuptools:command='report_setup_data'
