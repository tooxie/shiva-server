# -*- coding: utf-8 -*-
import mimetypes
import os
import sys
import re

from flask import abort, Flask, Response, request, send_file

from shiva.config import Configurator
from shiva.utils import get_logger

app = Flask(__name__)
app.config.from_object(Configurator())

log = get_logger()


def get_absolute_path(relative_path):
    for mdir in app.config.get('MEDIA_DIRS', []):
        full_path = os.path.join(mdir.root, relative_path)

        for excluded in mdir.get_excluded_dirs():
            if full_path.startswith(excluded):
                return None

        if os.path.exists(full_path):
            return full_path

    return None


@app.route('/<path:relative_path>')
def serve(relative_path):
    absolute_path = get_absolute_path(relative_path)
    if not absolute_path:
        abort(404)

    range_header = request.headers.get('Range', None)
    if not range_header:
        return send_file(absolute_path)

    size = os.path.getsize(absolute_path)
    start_byte = 0
    end_byte = None

    m = re.search('(\d+)-(\d*)', range_header)
    g = m.groups()

    if g[0]:
        start_byte = int(g[0])
    if g[1]:
        end_byte = int(g[1])

    length = size - start_byte
    if end_byte is not None:
        length = end_byte - start_byte

    content = None
    with open(absolute_path, 'rb') as f:
        f.seek(start_byte)
        content = f.read(length)

    response = Response(content,
                        206,
                        mimetype=mimetypes.guess_type(absolute_path)[0],
                        direct_passthrough=True)
    response.headers.add('Content-Range', 'bytes %d-%d/%d' % (
        start_byte, start_byte + length - 1, size))
    response.headers.add('Accept-Ranges', 'bytes')

    return response


def main():
    try:
        port = int(sys.argv[1])
    except:
        port = 8001

    log.warn("""
    +------------------------------------------------------------+
    | This is a *development* server, for testing purposes only. |
    | Do NOT use in a live environment.                          |
    +------------------------------------------------------------+
    """)

    app.run('0.0.0.0', port=port, debug=False)

if __name__ == '__main__':
    main()
