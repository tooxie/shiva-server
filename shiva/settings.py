# -*- coding: utf-8 -*-
from os import path

PROJECT_ROOT = path.dirname(path.abspath(__file__))

DEBUG = True
SQLALCHEMY_DATABASE_URI = 'sqlite:///%s/stream.db' % PROJECT_ROOT
SECRET_KEY = '-'  # TODO: Move this option to a file that can be edited in a
                  # per-installation basis.
