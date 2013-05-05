# -*- coding: utf-8 -*-
"""
Dropbox™ backend
================

This module adds support for reading files from Dropbox™ accounts. You will
need an app key and secret, which you can obtain from the `Dropbox developer
website <https://www.dropbox.com/developers/apps>`_.

It requires the following settings:

* DROPBOX_APP_KEY
* DROPBOX_APP_SECRET
* DROPBOX_ACCESS_TYPE
"""
from dropbox import client, rest, session
from flask import current_app as app

DROPBOX_APP_KEY = app.config['DROPBOX_APP_KEY']
DROPBOX_APP_SECRET = app.config['DROPBOX_APP_SECRET']
DROPBOX_ACCESS_TYPE = app.config['DROPBOX_ACCESS_TYPE']


class DropboxBackend(object):

    def __init__(self):
        session = session.DropboxSession(APP_KEY, APP_SECRET, ACCESS_TYPE)
        request_token = sess.obtain_request_token()

        # Make the user sign in and authorize this token
        url = sess.build_authorize_url(request_token)
        print "url:", url
        print "Please authorize in the browser. After you're done, hit enter."
        raw_input()

        # This will fail if the user didn't visit the above URL and hit 'Allow'
        access_token = sess.obtain_access_token(request_token)
