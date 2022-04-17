# -*- coding: utf-8 -*-
#
#   This file is part of Condiment.
#   Copyright (C) 2020-2022, Condiment Developers.
#
#   Please refer to AUTHORS.rst for a complete list of Copyright holders.
#
#   Condiment is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   Condiment is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program. If not, see http://www.gnu.org/licenses.

"""

This module contains common juju Exceptions.

This file holds the generic errors which are sensible for several
areas of juju.

"""


class CondimentError(Exception):

    """

    All errors in juju are subclasses of this.

    This error should not be raised by itself, though, since it means
    pretty much nothing.  It's useful mostly as something to catch instead.

    """


class CannotIdentifyDistribution(CondimentError):
    """"""

    def __str__(self):
        return ("We could not identify your distribution.")


class UnsupportedDistribution(CondimentError):
    """"""

    def __str__(self):
        return ("Your distribution is not supported.")
