# -*- coding: utf-8 -*-
from flask import g, request, current_app as app
from flask.ext.restful import abort, Resource

from shiva.auth.const import Roles
from shiva.constants import HTTP
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
        abort(HTTP.UNAUTHORIZED)

    g.user = user


class AuthResource(Resource):
    def post(self):
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if not user or not user.verify_password(password):
            abort(HTTP.UNAUTHORIZED)

        return {
            'token': user.generate_auth_token(),
        }


class ACLMixin(object):
    """
    This mixin enhances Resources with ACL capabilities. Every resource that
    contains an `allow` attribute (which should be a list of roles, whose valid
    values are defined in `shiva.auth.Roles`) will be authenticated against the
    currently logged in user. If no `allow` attribute is present, the resource
    is considered to be unrestricted.

    This check will be done right before any attribute in the class is called.
    In pseudo code, the check is as follows:

    .. code::
        if ALLOW_ANONYMOUS_ACCESS:
            call() unless SHIVA in self.allow
        else:
            if self.allow:
                if g.user.role in self.allow:
                    call()
            else:
                call()

        abort()

    The resources restricted to SHIVA users are very expensive to compute,
    therefore its access is restricted even when ALLOW_ANONYMOUS_ACCESS is set
    to True.
    """

    def __getattribute__(self, name):
        def allow_anonymous():
            return app.config.get('ALLOW_ANONYMOUS_ACCESS', False)

        attr = object.__getattribute__(self, name)
        if hasattr(attr, '__call__'):
            if hasattr(self, '_allowed') and self._allowed:
                return attr

            if hasattr(self, 'allow'):
                if allow_anonymous():
                    self._allowed = True  # DEBUG

                    if Roles.SHIVA in self.allow:
                        if g.user and g.user.role in self.allow:
                            self._allowed = True
                else:
                    if g.user and g.user.role in self.allow:
                        self._allowed = True
            else:
                if allow_anonymous():
                    self._allowed = True

            if not hasattr(self, '_allowed') or not self._allowed:
                self._allowed = False
                abort(HTTP.FORBIDDEN)

        return attr
