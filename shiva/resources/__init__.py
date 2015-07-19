# -*- coding: utf-8 -*-
from shiva.auth import AuthResource
from shiva.resources.base import (
    ArtistResource, AlbumResource, TrackResource, UserResource,
    PlaylistResource, PlaylistTrackResource)
from shiva.resources.static import AboutResource, ClientResource
from shiva.resources.dynamic import (
    ConvertResource, LyricsResource, RandomResource, ShowsResource,
    WhatsNewResource)
from shiva.sync import SyncResource
