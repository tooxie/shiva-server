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
api.add_resource(resources.ArtistResource, '/artists', '/artists/<int:id>',
                 '/artists/<slug>', endpoint='artists')
api.add_resource(resources.ShowsResource, '/artists/<int:id>/shows',
                 '/artists/<slug>/shows', endpoint='shows')

# Albums
api.add_resource(resources.AlbumResource, '/albums', '/albums/<int:id>',
                 '/albums/<slug>', endpoint='albums')

# Tracks
api.add_resource(resources.TrackResource, '/tracks', '/tracks/<int:id>',
                 '/tracks/<slug>', endpoint='tracks')
api.add_resource(resources.LyricsResource, '/tracks/<int:id>/lyrics',
                 '/tracks/<slug>/lyrics', endpoint='lyrics')
api.add_resource(resources.ConvertResource, '/tracks/<int:id>/convert',
                 '/tracks/<slug>/convert', endpoint='convert')

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
        response.headers['Access-Control-Allow-Headers'] = \
            'Accept, Content-Type, Origin, X-Requested-With'

    return response


def main():
    try:
        port = int(sys.argv[1])
    except:
        port = 9002

    app.run(host='0.0.0.0', port=port, debug=True)


if __name__ == '__main__':
    main()
