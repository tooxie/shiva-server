# -*- coding: utf-8 -*-
from nose import tools as nose
import os
import tempfile
import unittest

from shiva import admin, app as shiva
from shiva.auth import Roles


class AdminTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        db_uri = 'sqlite:///%s' % self.db_path
        shiva.app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
        shiva.app.config['TESTING'] = True

        self.ctx = shiva.app.test_request_context()
        self.ctx.push()

        shiva.db.create_all()

    def tearDown(self):
        self.ctx.pop()
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def get_payload(self):
        return {
            'email': 'test@mail.com',
            'password': 'p4ssw0rd',
            'is_active': True,
            'is_admin': False,
            'interactive': False,
        }

    def test_user_creation(self):
        user = admin.create_user(**self.get_payload())

        nose.ok_(user.pk is not None)
        nose.eq_(user.is_active, True)
        nose.eq_(user.role, Roles.USER)

    def test_user_activation(self):
        params = self.get_payload()
        params['is_active'] = False

        user = admin.create_user(**params)
        nose.eq_(user.is_active, False)

        admin.activate_user(user.pk)

        nose.eq_(user.is_active, True)

    def test_user_deactivation(self):
        user = admin.create_user(**self.get_payload())
        nose.eq_(user.is_active, True)

        admin.deactivate_user(user.pk)

        nose.eq_(user.is_active, False)

    def test_user_deletion(self):
        user = admin.create_user(**self.get_payload())
        nose.ok_(user.pk is not None)

        admin.delete_user(user.pk)

        nose.ok_(admin.get_user(user.pk) is None)
