# -*- coding: utf-8 -*-
from mock import Mock
from nose import tools as nose
import unittest

from shiva.config import Configurator
from shiva import exceptions as exc


class ConfigTestCase(unittest.TestCase):

    def test_no_config(self):
        Configurator.from_xdg_config = Mock(return_value=False)
        Configurator.from_env = Mock(return_value=False)
        Configurator.from_local = Mock(return_value=False)

        nose.assert_raises(exc.NoConfigFoundError, Configurator)
