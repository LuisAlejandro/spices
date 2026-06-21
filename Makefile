#!/usr/bin/env make -f
# -*- makefile -*-

SHELL = bash -e
img_hash = $(shell docker images -q luisalejandro/spices:latest)
exec_on_docker = docker compose \
	-p spices -f docker-compose.yml exec \
	--user spices app

# Release configuration
VERSION_TYPE ?= patch
APP_NAME ?= spices

define BROWSER_PYSCRIPT
import os, webbrowser, sys
try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT
BROWSER := python3 -c "$$BROWSER_PYSCRIPT"

help:
	@echo "clean - remove all build, test, coverage and Python artifacts"
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "clean-test - remove test and coverage artifacts"
	@echo "lint - check style with flake8"
	@echo "format - apply Python formatting (autoflake, autopep8)"
	@echo "test - run tests with coverage"
	@echo "test-all - run tests on every Python version with tox"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "docs - generate Sphinx HTML documentation, including API docs"
	@echo "release - package and upload a release"
	@echo "dist - package"
	@echo "install - install the package to the active Python's site-packages"

clean: clean-build clean-pyc clean-test clean-docs

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/

clean-docs:
	rm -fr docs/_build

lint: start
	@$(exec_on_docker) tox -e lint

format: start
	@$(exec_on_docker) autoflake --in-place --recursive --remove-all-unused-imports --remove-unused-variables --ignore-init-module-imports spices
	@$(exec_on_docker) autopep8 --in-place --recursive --aggressive --aggressive spices

test: start
	@$(exec_on_docker) tox -e coverage

test-all: start
	@$(exec_on_docker) tox

coverage: start
	@$(exec_on_docker) coverage run --source spices -m unittest -v -f
	@$(exec_on_docker) coverage report -m
	@$(exec_on_docker) coverage html
	$(BROWSER) htmlcov/index.html

docs:
	@$(exec_on_docker) make -C docs clean
	@$(exec_on_docker) make -C docs html
	$(BROWSER) docs/_build/html/index.html

servedocs: docs start
	@$(exec_on_docker) watchmedo shell-command -p '*.rst' -c 'make -C docs html' -R -D .

dist: clean start
	@$(exec_on_docker) python3 -m build
	ls -l dist

install: clean start
	@$(exec_on_docker) pip3 install .

console: start
	@$(exec_on_docker) bash

virtualenv: start
	@python3 -m venv --clear ./virtualenv
	@./virtualenv/bin/python3 -m pip install --upgrade pip
	@./virtualenv/bin/python3 -m pip install --upgrade setuptools
	@./virtualenv/bin/python3 -m pip install --upgrade wheel
	@./virtualenv/bin/python3 -m pip install -r requirements.txt -r requirements-dev.txt

# >>> rosey-maintainer:ops-docker BEGIN
# Managed by rosey-maintainer-tools 0.2.0. Do not edit directly.

PROJECT_NAME ?= spices
all_ps_hashes = $(shell docker ps -q)

image:
	@docker compose -p $(PROJECT_NAME) -f docker-compose.yml build \
		--build-arg UID=$(shell id -u) \
		--build-arg GID=$(shell id -g)

start:
	@if [ -z "$(img_hash)" ]; then\
		make image;\
	fi
	@docker compose -p $(PROJECT_NAME) -f docker-compose.yml up \
		--remove-orphans --no-build --detach

stop:
	@docker compose -p $(PROJECT_NAME) -f docker-compose.yml stop

down:
	@docker compose -p $(PROJECT_NAME) -f docker-compose.yml down \
		--remove-orphans

destroy:
	@echo
	@echo "WARNING!!!"
	@echo "This will stop and delete all containers, images and volumes related to this project."
	@echo
	@read -p "Press ctrl+c to abort or enter to continue." -n 1 -r
	@docker compose -p $(PROJECT_NAME) -f docker-compose.yml down \
		--rmi all --remove-orphans --volumes

cataplum:
	@echo
	@echo "WARNING!!!"
	@echo "This will stop and delete all containers, images and volumes present in your system."
	@echo
	@read -p "Press ctrl+c to abort or enter to continue." -n 1 -r
	@if [ -n "$(all_ps_hashes)" ]; then\
		docker kill $(shell docker ps -q);\
	fi
	@docker compose -p $(PROJECT_NAME) -f docker-compose.yml down \
		--rmi all --remove-orphans --volumes
	@docker system prune -a -f --volumes
# <<< rosey-maintainer:ops-docker END

# >>> rosey-maintainer:ops-release BEGIN
# Managed by rosey-maintainer-tools 0.2.0. Do not edit directly.

release:
	@./scripts/release.sh $${VERSION_TYPE}

release-patch:
	@./scripts/release.sh patch $${APP_NAME}

release-minor:
	@./scripts/release.sh minor $${APP_NAME}

release-major:
	@./scripts/release.sh major $${APP_NAME}


release-preflight: start


	@make lint

	@make format

	@make test



undo-release:
	@: "$${VERSION:?Set VERSION=x.y.z before running make undo-release}"
	@VERSION=$${VERSION} ./scripts/rollback.sh release
# <<< rosey-maintainer:ops-release END

.PHONY: help clean clean-build clean-pyc clean-test clean-docs lint format test test-all coverage docs servedocs dist install console virtualenv image start stop down destroy cataplum release release-patch release-minor release-major release-preflight undo-release
