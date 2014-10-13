# -*- coding: utf-8 -*-
from flask import g, request
from flask.ext.restful import abort, Resource

from shiva.models import User


def verify_credentials(app):
    g.user = None

    if request.path == '/users/login/':
        return None

    if app.config.get('ALLOW_ANONYMOUS_ACCESS', False):
        return None

    token = request.args.get('token', '')
    user = User.verify_auth_token(token)

    if not user:
        abort(401)

    g.user = user


class AuthResource(Resource):
    def post(self):
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if not user or not user.verify_password(password):
            abort(401)

        return {
            'token': user.generate_auth_token(),
        }
