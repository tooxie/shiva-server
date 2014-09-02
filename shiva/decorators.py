# -*- coding: utf-8 -*-
from functools import wraps

from flask import current_app as app, g, request
from flask.ext.restful import abort


def allow_method(func=None):
    """Checks if the method is globally allowed, raising a 405 if not.
    """

    def wrapped(func):
        @wraps(func)
        def decorated(*args, **kwargs):
            allow_delete = app.config.get('ALLOW_DELETE', False)
            if func.func_name == 'delete' and not allow_delete:
                abort(405)

            return func(*args, **kwargs)

        return decorated

    if func:
        return wrapped(func)

    return wrapped


def allow_origins(func=None, custom_origins=None):
    """
    Add headers for Cross-origin resource sharing based on
    `CORS_ALLOWED_ORIGINS` in config, or parameters passed to the decorator.
    `CORS_ALLOWED_ORIGINS` can be a list of allowed origins or `"*"` to allow
    all origins.

    """

    def wrapped(func):
        def _get_origin(allowed_origins, origin):
            """ Helper method to discover the proper value for
            Access-Control-Allow-Origin to use.

            If the allowed origin is a string it will check if it's '*'
            wildcard or an actual domain. When a tuple or list is given
            instead, it will look for the current domain in the list. If any of
            the checks fail it will return False.

            """

            if type(allowed_origins) in (str, unicode):
                if allowed_origins == '*' or allowed_origins == origin:
                    return allowed_origins

            elif type(allowed_origins) in (list, tuple):
                if origin in allowed_origins:
                    return origin

            return False

        @wraps(func)
        def decorated(*args, **kwargs):
            origin = request.headers.get('Origin')

            # `app.config.get('CORS_ALLOWED_ORIGINS', [])` should really be the
            # default option in `def allow_origins` for `custom_origins` but
            # that would use `app` outside of the application context
            allowed_origins = custom_origins or \
                app.config.get('CORS_ALLOWED_ORIGINS', [])

            # Actual headers are added in `after_request`
            g.cors = _get_origin(allowed_origins, origin)

            return func(*args, **kwargs)

        return decorated

    if func:
        return wrapped(func)

    return wrapped
