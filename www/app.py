# -*- coding: utf-8 -*-
from flask import Flask, Response, request

import config

import urllib

app = Flask(__name__)
app.config.from_object(config)

@app.route('/')
@app.route('/<path:path>')
def index(path=None):
    if path:
        uri = '/'.join(((app.config['NODEJS_URL']), path))
    else:
        uri = app.config['NODEJS_URL']

    if request.query_string:
        uri = '?'.join((uri, request.query_string))

    _request = urllib.urlopen(uri)

    mimetype = _request.headers.get('Content-Type', 'text/html')
    mimetype = mimetype.split(';')[0].strip()

    return Response(_request.read(), status=_request.getcode(),
                    mimetype=mimetype)

@app.route('/api/<path:path>')
def api_call(path):
    """
    """
    uri = '%s/%s' % (app.config['SHIVA_URL'], path)

    if request.query_string:
        uri = '?'.join((uri, request.query_string))

    _request = urllib.urlopen(uri)

    return Response(_request.read(), status=_request.getcode(),
                    mimetype='application/javascript')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
