# -*- coding: utf-8 -*-
from flask import Response

from shiva import models


def download(track_id, ext):
    """
    """
    if ext != 'mp3':
        return Response('', status=404)

    track = models.Track.query.get(track_id)
    track_file = open(track.get_path(), 'r')
    filename_header = (
        'Content-Disposition', 'attachment; filename="%s.mp3"' % track.title
    )

    return Response(response=track_file.read(), mimetype='audio/mpeg',
                    headers=[filename_header])
