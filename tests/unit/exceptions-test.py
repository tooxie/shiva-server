# -*- coding: utf-8 -*-
from nose import tools as nose
import unittest

from shiva import exceptions as exc


class ExceptionsTestCase(unittest.TestCase):

    def test_invalid_mimetype_error(self):
        error = exc.InvalidMimeTypeError('audio/mp3')
        nose.eq_(error.__str__(), "Invalid mimetype 'audio/mp3'")

    def test_no_config_found_error(self):
        error = exc.NoConfigFoundError()
        nose.assert_not_equal(error.__str__(), '')
