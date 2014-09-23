# -*- coding: utf-8 -*-
from nose import tools as nose
import unittest

from shiva.utils import parse_bool, randstr


class ParseBoolTestCase(unittest.TestCase):

    @nose.raises(ValueError)
    def test_none_raises_value_error(self):
        val = parse_bool(None)

    def test_false_strings(self):
        nose.ok_(parse_bool('false') == False)
        nose.ok_(parse_bool('0') == False)
        nose.ok_(parse_bool('') == False)

    def test_true_strings(self):
        nose.ok_(parse_bool('true') == True)
        nose.ok_(parse_bool('1') == True)

    def test_random_strings(self):
        nose.ok_(parse_bool('derp') == True)
        nose.ok_(parse_bool('_') == True)
        nose.ok_(parse_bool('.') == True)
        nose.ok_(parse_bool('$') == True)


class RandomStringTestCase(unittest.TestCase):

    def test_empty_string(self):
        nose.ok_(randstr(0) == '')

    def test_short_string(self):
        nose.ok_(len(randstr(1)) == 1)

    def test_long_string(self):
        nose.ok_(len(randstr(128)) == 128)
