from functools import wraps
from flask import g, request, make_response
from flask import current_app as app


def allow_origins(func=None, custom_origins=None):
    """
    Add headers for Cross-origin resource sharing based on `ALLOWED_ORIGINS`
    in config, or parameters passed to the decorator. `ALLOWED_ORIGINS` can be
    a list of allowed origins or `"*"` to allow all origins.
    """
    def wrapped(func):
        @wraps(func)
        def decorated(*args, **kwargs):
            origin = request.headers.get('Origin')

            # `origins=app.config.get('ALLOWED_ORIGINS', [])` should really be
            # the default option in `def allow_origins` but that would use
            # `app` outside of the application context
            origins = custom_origins or app.config.get('ALLOWED_ORIGINS', [])

            # Actual headers are added in `after_request`, unless it's an
            # OPTIONS request.
            if origins == '*':
                g.cors = '*'
            elif origin in origins:
                g.cors = origin
            else:
                g.cors = False

            if request.method == 'OPTIONS':
                response = make_response('ok')
                response.headers['Access-Control-Allow-Origin'] = origin
                response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
                return response
            return func(*args, **kwargs)
        return decorated
    if func:
        return wrapped(func)
    else:
        return wrapped
