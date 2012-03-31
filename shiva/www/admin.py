# -*- coding: utf-8 -*-
from shiva.www import app
from shiva.models import (get_session, engine, Hash, ID3Tag, Song, SongTag,
                          TagContent, TagGroup)
from flask.ext.admin import create_admin_blueprint
from flask.ext.admin.datastore.sqlalchemy import SQLAlchemyDatastore
from sqlalchemy.orm import scoped_session, sessionmaker

db_session = scoped_session(sessionmaker(bind=engine))

datastore = SQLAlchemyDatastore((Hash, ID3Tag, Song, SongTag, TagContent,
                                 TagGroup), db_session, exclude_pks=False)
admin_blueprint = create_admin_blueprint(datastore)
app.register_blueprint(admin_blueprint, url_prefix='/admin')
