# -*- coding: utf-8 -*-
import sys

from flask import Flask, g, request
from flask.ext.restful import Api
from flask.ext.compress import Compress

from shiva import resources
from shiva.auth import verify_credentials
from shiva.config import Configurator
from shiva.models import db
from shiva.utils import randstr

app = Flask(__name__)
app.config.from_object(Configurator())
db.app = app
db.init_app(app)

# Serve all requests gzipped
if app.config.get('USE_GZIP', True):
    Compress(app)

# RESTful API
api = Api(app)

# Artists
api.add_resource(resources.ArtistResource, '/artists/', '/artists/<id>/',
                 endpoint='artists')
api.add_resource(resources.ShowsResource, '/artists/<id>/shows/',
                 endpoint='shows')

# Albums
api.add_resource(resources.AlbumResource, '/albums/', '/albums/<id>/',
                 endpoint='albums')

# Tracks
api.add_resource(resources.TrackResource, '/tracks/', '/tracks/<id>/',
                 endpoint='tracks')
api.add_resource(resources.LyricsResource, '/tracks/<id>/lyrics/',
                 endpoint='lyrics')
api.add_resource(resources.ConvertResource, '/tracks/<id>/convert/',
                 endpoint='convert')

# Playlists
api.add_resource(resources.PlaylistTrackResource, '/playlists/<id>/<verb>/',
                 endpoint='playlist_tracks')
api.add_resource(resources.PlaylistResource, '/playlists/', '/playlists/<id>/',
                 endpoint='playlists')

# Users
api.add_resource(resources.AuthResource, '/users/login/', endpoint='auth')
api.add_resource(resources.UserResource, '/users/', '/users/<id>/',
                 endpoint='users')

# Shiva-Shiva
api.add_resource(resources.SyncResource, '/sync/', '/sync/<since>/',
                 endpoint='sync')

# Other
api.add_resource(resources.RandomResource, '/random/<resource_name>/',
                 endpoint='random')
api.add_resource(resources.WhatsNewResource, '/whatsnew/', endpoint='whatsnew')
api.add_resource(resources.ClientResource, '/clients/', endpoint='client')
api.add_resource(resources.AboutResource, '/about/', endpoint='about')


@app.before_request
def before_request():
    g.db = db

    # auth
    verify_credentials(app)


@app.after_request
def after_request(response):
    if getattr(g, 'cors', False):
        response.headers['Access-Control-Allow-Origin'] = g.cors
        response.headers['Access-Control-Allow-Headers'] = \
            'Accept, Content-Type, Origin, X-Requested-With'

    return response


def main():
    if not app.config.get('SECRET_KEY'):
        error = ('Error: Please define a `SECRET_KEY` in your config file.\n'
                 'You can use the following one:\n\n    %s\n' % randstr(64))
        sys.stderr.write(error)
        sys.exit(1)

    try:
        port = int(sys.argv[1])
    except:
        port = 9002

    app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    main()
