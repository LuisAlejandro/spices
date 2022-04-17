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

condiment.common.utils
===================

This module contains common and low level functions to all modules in Condiment.

"""


# Taken from: http://stackoverflow.com/a/2158532
def flatten_list(originlist=[]):
    """

    Convert a nested list into one combined list.

    :param originlist: a list object with (optionally) nested list.
    :return: a generator with all nested lists combined.
    :rtype: a generator.

    .. versionadded:: 0.1

    >>> originlist = [[['1'], [[2, 3, 4], [5, 6, [7]], [8]]], [9, 10, 11, 12], [13, 14]]
    >>> list(flatten_list(originlist))
    ['1', 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
    >>> originlist = []
    >>> list(flatten_list(originlist))
    []

    """
    from collections import Iterable
    for el in originlist:
        if isinstance(el, Iterable) and not isinstance(el, basestring):
            for sub in flatten_list(el):
                yield sub
        else:
            yield el
