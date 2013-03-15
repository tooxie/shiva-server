# -*- coding: utf-8 -*-
"""
cat /dev/brain
==============

Just a series of thoughts about how the Flask-Restless' API could be modified
to allow for the creation of non db-backed resources. None of this has been
through any serious thought about fesibility, they are just random ideas.
"""
from flask import Flask
from flask.ext.restless import APIManager, Resource
from flapi.models import session, Audio

app = Flask(__name__)


class SongResource(Resource):
    """
    This approach is based on
    https://code.google.com/p/django-rest-interface/wiki/RestifyDjango
    and
    http://django-tastypie.readthedocs.org/en/latest/resources.html
    """

    def create(self):
        pass

    def read(self, id=None, ids_only=False, nesting_levels=1):
        """
        The ids_only parameter would force the method to return only the IDs of
        the matching element. Useful for nesting.

        Not sure about the nesting_levels.
        """

        pass

    def update(self, *args, **kwargs):
        pass

    def delete(self, id):
        pass

    def patch(self):
        pass

    def head(self):
        pass

    def options(self):
        pass

    def connect(self):
        raise NotImplementedError

    def trace(self):
        raise NotImplementedError

    def validator(self, data):
        """
        Validates the data sent by the client. Run always before every method.
        Maybe could be turn into a decorator (like before_request)
        """

        pass

    def authorize(self):
        pass

    def get_format(self):
        """
        /api/songs.json
        /api/songs?format=json
        Accept: application/json
        """

        raise NotImplementedError


# --


class SongResource(Resource):
    """
    A less django-ish approach.
    """

    # A more SQLAlchemy-ish approach.
    __basemodel__ = Audio
    __resource__ = '/songs/'

    # This method decorator should be defined once and only once per Verb. It
    # would tell the Resource how to read/write. Me gusta.
    @method('GET')
    def get_all_or_one(self, id=None):
        pass

    @method(['POST', 'PUT', 'PATCH'])
    def write(self, data):
        pass

    def authorize(self):
        pass

    def get_format(self):
        pass


# --


# Registering the Route. For both previous examples.
# Maybe decorate the class? /me not likes
@app.route('/songs/')
class SongResource(Resource):
    pass


# Use the add_url_rule decorator.
app.add_url_rule('/songs/', 'songs', SongResource)

# Downside: Duplication.
app.add_url_rule('/songs/<int:song_id>', 'song', SongResource)

# Possible solution, delegate to the Resource?
SongResource.create_rules(app)

# Or do it in batch.
api = APIManager(app, session=session)
api.resources([SongResource, ArtistResouce, SomeOtherResource])
api.create_rules(app)  # Explicit is better than implicit


# --


# This is a more flasky approach. Simple, extensible.
# ME GUSTA
api = APIManager(app, session=session)

@api.resource('/songs')
def songs(song_id=None):
    pass

# Note that the decorator now is the previous function.
@songs.method('PUT')
def save_song(data):
    pass

@songs.authorize
def check_permissions():
    pass

# This method should rarely be ovewritten.
@songs.get_format
def get_format():
    pass

# (...)

# The problem I see with this is how to build a resource from existing models
# using this approach. Doesn't look very straightforward at first.
# Maybe...
api.resource(Audio, methods=['GET', 'POST', 'DELETE'])


# --


# Traversal
# =========

# As seen on:
# http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/traversal.html
# and
# http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/resources.html


class RootResource(object):
    """
    """

    __name__ = ''
    __parent__ = None


class SongResource(object):
    """
    """

    def __resource_url__(self):
        from flask import request

        return request.base_url

from flask.ext.restless import inside, lineage, find_root


class Thing(object):
    pass

a = Thing()
b = Thing()
b.__parent__ = a

inside(b, a)  # >>> True
inside(a, b)  # >>> False

list(lineage(b))
# >>> [ <Thing object at b>, <Thing object at a>]

find_root(b)
# >>> a


# --


# The present way:
manager = APIManager(app, session=session)
# Not a big fan of the 'create_api' method name.
manager.create_api(Audio, methods=['GET', 'POST', 'DELETE'])


# --


"""
Unsolved issues
---------------

* Define nested resources.
    * Serializers?
* Permissions for nested resources.
* Depth of nested resources.
* Definition of formats to retrieve.
* Multiple API versions.

Ideas:
* https://github.com/tryolabs/django-tastypie-extendedmodelresource#readme
* http://django-rest-framework.org/tutorial/1-serialization.html
* http://django-rest-framework.org/api-guide/serializers.html
* https://github.com/ametaireau/flask-rest/

"""

# :wq
