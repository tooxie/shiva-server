# -*- coding: utf-8 -*-
from nose import tools as nose
import unittest

import shiva


class MetaDataTestCase(unittest.TestCase):

    def test_version(self):
        nose.eq_(shiva.get_version(), shiva.__version__)

    def test_contributors(self):
        nose.eq_(shiva.get_contributors(), shiva.__contributors__)
