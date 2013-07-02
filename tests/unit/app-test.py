# -*- coding: utf-8 -*-
from nose import tools as nose
import unittest
from mock import Mock

from shiva import app


class AppTestCase(unittest.TestCase):

    def setUp(self):
        app.app.run = Mock()

    def test_main(self):
        app.main()
        nose.assert_true(app.app.run.called)
