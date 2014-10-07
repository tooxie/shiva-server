# -*- coding: utf-8 -*-
from flask.ext.restful import Resource, Response

from shiva.auth import Roles, ACLMixin
from shiva.models import Track
from shiva.resources import serializers


class SyncResource(Resource, ACLMixin):
    """
    Endpoint responsible for all the shiva2shiva communication.
    """
    allow = [Roles.SHIVA]

    def get(self, since=None):
        return serializers.TrackSerializer(Track.query.all()).to_json()
