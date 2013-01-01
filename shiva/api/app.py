# -*- coding: utf-8 -*-
from flask import Flask
from flask.ext.restful import Api

from shiva.api.models import db
from shiva.api import resources

app = Flask(__name__)
app.config.from_object('shiva.api.config')

db.app = app
db.init_app(app)

api = Api(app)

app.add_url_rule('/track/<int:track_id>/download.<ext>', 'download',
                 'shiva.api.views.download')

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
