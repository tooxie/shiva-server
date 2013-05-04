# -*- coding: utf-8 -*-
import sys

from flask import Flask, g, request
from flask.ext.restful import Api

from shiva import resources
from shiva.config import Configurator
from shiva.models import db

app = Flask(__name__)
app.config.from_object(Configurator())
db.app = app
db.init_app(app)

# RESTful API
api = Api(app)

# Artists
api.add_resource(resources.ArtistResource, '/artists',
                 '/artist/<int:artist_id>', '/artist/<artist_slug>',
                 endpoint='artist')
api.add_resource(resources.ShowsResource, '/artist/<int:artist_id>/shows',
                 '/artist/<artist_slug>/shows', endpoint='shows')

# Albums
api.add_resource(resources.AlbumResource, '/albums', '/album/<int:album_id>',
                 '/album/<album_slug>', endpoint='album')

# Tracks
api.add_resource(resources.TracksResource, '/tracks', '/track/<int:track_id>',
                 '/track/<track_slug>', endpoint='track')
api.add_resource(resources.LyricsResource, '/track/<int:track_id>/lyrics',
                 '/track/<track_slug>/lyrics', endpoint='lyrics')
api.add_resource(resources.ConvertResource, '/track/<int:track_id>/convert',
                 '/track/<track_slug>/convert', endpoint='convert')

# Other
api.add_resource(resources.RandomResource, '/random/<resource_name>',
                 endpoint='random')
api.add_resource(resources.WhatsNewResource, '/whatsnew', endpoint='whatsnew')
api.add_resource(resources.ClientResource, '/clients', endpoint='client')
api.add_resource(resources.AboutResource, '/about', endpoint='about')


@app.before_request
def before_request():
    g.db = db


@app.after_request
def after_request(response):
    if getattr(g, 'cors', False):
        response.headers['Access-Control-Allow-Origin'] = g.cors
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'

    return response


def main():
    try:
        port = int(sys.argv[1])
    except:
        port = 9002

    app.run(host='0.0.0.0', port=port, debug=True)


if __name__ == '__main__':
    main()
