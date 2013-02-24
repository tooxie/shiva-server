# -*- coding: utf-8 -*-
from shiva.media import get_duplicates_path

DEBUG = True

SQLALCHEMY_DATABASE_URI = 'sqlite:///shiva.db'
DUPLICATES_PATH = get_duplicates_path
