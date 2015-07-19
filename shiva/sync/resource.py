# -*- coding: utf-8 -*-
from flask.ext.restful import Resource, Response

from shiva.auth import Roles, ACLMixin
from shiva.models import Track
from shiva.resources import serializers


class SyncResource(Resource, ACLMixin):
    """
    Endpoint responsible for all the shiva2shiva communication. As a first
    version the communication will be done through gzipped JSON over HTTP. This
    works fine for small to medium-sized music collections, but it won't scale
    once the DB query becomes slow and the resulting JSON massive to handle.

    We have so far no data that helps us draw the line between what is
    manageable and which music collection size is too big. That's why we
    decided to go with the easiest solution and optimize when we actually hit a
    wall. If you, however, happen to know a better approach and want to
    implement it, feel free to issue a PR.
    """
    allow = [Roles.SHIVA]

    def get(self, since=None):
        tracks = Track.query.all()

        return serializers.TrackSerializer(tracks).to_json(recursive=True)
