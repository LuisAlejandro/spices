#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import doctest

if sys.version_info[:2] == (2, 6):
    import unittest2 as unittest
else:
    import unittest


def load_tests(loader, tests, pattern):
    tests.addTests(doctest.DocTestSuite('condiment.utils'))
    return tests


if __name__ == '__main__':
    sys.exit(unittest.main())
