# -*- coding: utf-8 -*-
from nose import tools as nose
import unittest

from shiva import http
from shiva.app import app


class HTTPTestCase(unittest.TestCase):

    def test_options_method_returns_json_response(self):
        with app.app_context():
            resource = http.Resource()
            nose.assert_true(isinstance(resource.options(), http.JSONResponse))
