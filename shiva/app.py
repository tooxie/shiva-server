# -*- coding: utf-8 -*-
from flask import Flask, g
from flask.ext.restful import Api

from shiva.models import db
from shiva import resources, views

app = Flask(__name__)
app.config.from_object('shiva.config')

db.app = app
db.init_app(app)

# URIs
app.add_url_rule('/track/<int:track_id>/download.<ext>', 'download',
                 views.download)

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

# Random
api.add_resource(resources.RandomResource, '/random/<resource_name>',
                 endpoint='random')

# Clients
api.add_resource(resources.ClientResource, '/clients', endpoint='client')


@app.before_request
def before_request():
    g.db = db

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9002, debug=True)
