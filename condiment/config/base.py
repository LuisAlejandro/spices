#!/usr/bin/env python
# -*- coding: utf-8 -*-

from condiment import BASEDIR
from condiment.common.utils import get_path

NAME = u'Condiment'
VERSION = (0, 1, 0, 'alpha', 1)
URL = u'http://github.com/condimentdev/condiment'
AUTHOR = u'Desarrolladores de Condiment'
AUTHOR_EMAIL = u'condimentdev@googlegroups.com'
DESCRIPTION = (u'Red social para la gestión de comunidades de Software Libre.')
LICENSE = u'GPL'

CONFDIR = BASEDIR + '/condiment/config'
BINDIR = BASEDIR
SHAREDIR = BASEDIR
DOCDIR = BASEDIR + '/condiment/data/docs'
LOCALEDIR = BASEDIR + '/condiment/i18n'
ICONDIR = BASEDIR + '/condiment/data/icons'
PACKAGECACHE = BASEDIR + '/packagecache'
CHARMSDIR = BASEDIR + '/condiment/data/charms'

CONTAINERS = 'vagrant'
