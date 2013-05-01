# -*- coding: utf-8 -*-
import mimetypes
import os
import sys

from flask import abort, Flask, Response

app = Flask(__name__)
app.config.from_object('shiva.config')
if os.environ.get('SHIVA_CONFIG'):
    app.config.from_envvar('SHIVA_CONFIG')

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

    content = file(absolute_path, 'r').read()
    mimetype = mimetypes.guess_type(absolute_path)[0]

    return Response(content, status=200, mimetype=mimetype)

def main():
    try:
        port = int(sys.argv[1])
    except:
        port = 8001

    print("""
    +------------------------------------------------------------+
    | This is a *development* server, for testing purposes only. |
    | Do NOT use in a live environment.                          |
    +------------------------------------------------------------+
    """)

    app.run('0.0.0.0', port=port, debug=False)

if __name__ == '__main__':
    main()
