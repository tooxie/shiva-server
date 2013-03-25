# -*- coding: utf-8 -*-
from flask import Response
from flask.ext.restful import abort

from shiva import models


def download(track_id, ext):
    """
    """
    if ext != 'mp3':
        return Response('', status=404)
    track = models.Track.query.get(track_id)
    if track is None:
        abort(404)
    track_file = open(track.get_path(), 'r')
    filename_header = (
        'Content-Disposition', 'attachment; filename="%s.mp3"' % track.title
    )

    return Response(response=track_file.read(), mimetype='audio/mpeg',
                    headers=[filename_header])
