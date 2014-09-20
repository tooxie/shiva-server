# -*- coding: utf-8 -*-
from math import ceil
import json

from flask import current_app as app, Response, request, g
from flask.ext import restful


from shiva.decorators import allow_origins, allow_method
from shiva.utils import parse_bool, unpack


class Resource(restful.Resource):
    def __new__(cls, *args, **kwargs):
        cls.method_decorators.append(allow_method)

        if app.config.get('CORS_ENABLED') is True:
            # Applies to all inherited resources
            cls.method_decorators.append(allow_origins)

        return super(Resource, cls).__new__(cls, *args, **kwargs)

    # Without this the shiva.decorator.allow_origins method won't get called
    # when issuing an OPTIONS request.
    def options(self, *args, **kwargs):
        return JSONResponse()

    def get(self, id=None, slug=None):
        """
        Handler for the GET method. Given, for example:

        /users
        /users/<id>

        if a db_model attribute exists in the resource pointing to the
        respective model of the resource, the class will try to fetch the
        requested instance by id or slug. If such attribute doesn't exist it
        will return a 405 (Method Not Allowed) status code.
        """

        result = None

        if id:
            result = self.marshal(self.full_tree(self._by_id(id)))
        elif slug:
            result = self.marshal(self.full_tree(self._by_slug(slug)))
        else:
            if not hasattr(self, 'db_model'):
                return restful.abort(405)

            result = self._all()

        return result

    def put(self, id=None):
        if not id:
            return restful.abort(405)

        if not hasattr(self, 'update'):
            return restful.abort(405)

        # TODO: Check permissions
        item = self._by_id(id)

        self.update(item)

    def delete(self, id=None):
        if not id:
            return restful.abort(405)

        item = self._by_id(id)

        g.db.session.delete(item)
        g.db.session.commit()

        return ''

    def _by_id(self, id):
        try:
            result = self.get_by_id(id)
        except:
            restful.abort(404)

        if not result:
            restful.abort(404)

        return result

    def get_by_id(self, id):
        return self.db_model.query.get(id)

    def _by_slug(self, slug):
        try:
            result = self.get_by_slug(slug)
        except:
            restful.abort(404)

        if not result:
            restful.abort(404)

        return result

    def get_by_slug(self, slug):
        return self.db_model.query.filter_by(slug=slug).first()

    def _all(self):
        result = self.get_all()

        return self.paginate(result)

    def get_all(self):
        return self.db_model.query  # all()

    def filter(self, queryset, filters):
        """
        This method is supposed to be overriden by its children, to define the
        options and filters available. The format is as follows:

        (
            ('get_param', 'filter_method'),
            ('artist', 'artist_filter'),
        )

        If the parameter 'get_param' is present in the GET query (e.g.
        /something/?get_param=1) it will call filter_method() on the object.
        """

        if not hasattr(self, 'get_filters'):
            return queryset

        options = request.args.to_dict()

        for attribute in self.get_filters():
            value = options.get(attribute[0])
            func = getattr(self, attribute[1])
            if value and func:
                queryset = func(queryset, value)

        return queryset

    def full_tree(self, result):
        if not hasattr(self, 'get_full_tree'):
            return result

        options = request.args.to_dict()
        full_tree = parse_bool(options.get('fulltree', ''))

        if full_tree:
            return self.get_full_tree(result)

        return result

    def marshal(self, result):
        if isinstance(result, dict):
            return result

        return restful.marshal(result, self.get_resource_fields())

    def paginate(self, queryset):
        options = request.args.to_dict()
        queryset = self.filter(queryset, options)

        try:
            page_number = int(options.get('page', 1))
        except ValueError:
            page_number = 1
        try:
            limit = int(options.get('page_size', 10))
        except ValueError:
            limit = 10
        offset = limit * (page_number - 1)

        count = queryset.count()
        total_pages = max(int(ceil(float(count) / float(limit))), 1)
        items = queryset.limit(limit).offset(offset).all()

        return {
            'item_count': count,
            'items': self.marshal(items),
            'page': page_number,
            'page_size': limit,
            'pages': total_pages,
        }


class JSONResponse(restful.Response):
    """
    A subclass of flask.Response that sets the Content-Type header by default
    to "application/json".
    """

    def __init__(self, *args, **kwargs):
        data, status, headers = unpack(args)

        params = {
            'mimetype': 'application/json',
            'response': data,
            'status': status,
            'headers': headers,
        }
        params.update(kwargs.copy())

        if status >= 400:
            params['response'] = restful.utils.error_data(status)

        if params['status'] == 200 and params['response'] == '':
            params['status'] = 204

        if isinstance(params['response'], dict):
            params['response'] = json.dumps(params['response'])

        super(JSONResponse, self).__init__(**params)
