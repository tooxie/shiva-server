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
                 '/artist/<int:artist_id>', endpoint='artist')
api.add_resource(resources.ShowsResource,
                 '/artist/<int:artist_id>/shows', endpoint='shows')

# Albums
api.add_resource(resources.AlbumResource, '/albums',
                 '/album/<int:album_id>', endpoint='album')

# Tracks
api.add_resource(resources.TracksResource, '/tracks',
                 '/track/<int:track_id>', endpoint='track')
api.add_resource(resources.LyricsResource,
                 '/track/<int:track_id>/lyrics', endpoint='lyrics')


@app.before_request
def before_request():
    g.db = db

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
