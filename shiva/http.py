from flask import current_app as app, Response
from flask.ext import restful

from shiva.decorators import allow_origins


class Resource(restful.Resource):
    def __new__(cls, *args, **kwargs):
        if app.config.get('CORS_ENABLED') is True:
            # Applies to all inherited resources
            cls.method_decorators = [allow_origins]

        return super(Resource, cls).__new__(cls, *args, **kwargs)

    # Without this the shiva.decorator.allow_origins method won't get called
    # when issuing an OPTIONS request.
    def options(self):
        return JSONResponse()


class JSONResponse(Response):
    """
    A subclass of flask.Response that sets the Content-Type header by default
    to "application/json".

    """

    def __init__(self, status=200, **kwargs):
        params = {
            'headers': [],
            'mimetype': 'application/json',
            'response': '',
            'status': status,
        }
        params.update(kwargs)

        super(JSONResponse, self).__init__(**params)
