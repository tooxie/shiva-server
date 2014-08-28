# -*- coding: utf-8 -*-
try:
    import unittest2 as unittest
except ImportError:
    import unittest
from nose import tools as nose

from shiva.fileserver import get_range_bytes


class ByteRangeTestCase(unittest.TestCase):
    def test_invalid_start_byte(self):
        nose.eq_(get_range_bytes('range=-100'), (0, 100))

    def test_invalid_end_byte(self):
        nose.eq_(get_range_bytes('range=0-'), (0, None))

    def test_no_bytes(self):
        nose.eq_(get_range_bytes('range='), (0, None))

    def test_no_input(self):
        nose.eq_(get_range_bytes(''), (0, None))

    def test_valid_range(self):
        nose.eq_(get_range_bytes('range=0-100'), (0, 100))
