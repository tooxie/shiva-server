# -*- coding: utf-8 -*-
import mimetypes
import os
import re
import sys

from flask import abort, Flask, Response, request, send_file

from shiva.config import Configurator
from shiva.utils import get_logger

app = Flask(__name__)
app.config.from_object(Configurator())

log = get_logger()
RANGE_RE = re.compile(r'(\d+)-(\d*)')


@app.after_request
def after_request(response):
    response.headers['Accept-Ranges'] = 'bytes'

    return response


def get_absolute_path(relative_path):
    for mdir in app.config.get('MEDIA_DIRS', []):
        full_path = os.path.join(mdir.root, relative_path)

        for excluded in mdir.get_excluded_dirs():
            if full_path.startswith(excluded):
                return None

        if os.path.exists(full_path):
            return full_path

    return None


def get_range_bytes(range_header):
    """
    Returns a tuple of the form (start_byte, end_byte) with the information
    provided by range_header. Defaults to (0, None) in case one of the provided
    values is not an int.

    """

    _range = RANGE_RE.search(range_header).groups()
    try:
        start_byte, end_byte = [int(bit) for bit in _range]
    except:
        start_byte = 0
        end_byte = None

    return (start_byte, end_byte)


@app.route('/<path:relative_path>')
def serve(relative_path):
    absolute_path = get_absolute_path(relative_path)
    if not absolute_path:
        abort(404)

    range_header = request.headers.get('Range', None)
    if not range_header:
        return send_file(absolute_path)

    size = os.path.getsize(absolute_path)
    start_byte, end_byte = get_range_bytes(range_header)
    length = (end_byte or size) - start_byte

    content = None
    with open(absolute_path, 'rb') as f:
        f.seek(start_byte)
        content = f.read(length)

    status_code = 206  # Partial Content
    mimetype = mimetypes.guess_type(absolute_path)[0]
    response = Response(content, status_code, mimetype=mimetype,
                        direct_passthrough=True)

    response.headers.add('Content-Range', 'bytes %d-%d/%d' % (
        start_byte, start_byte + length - 1, size))

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
