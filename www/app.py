# -*- coding: utf-8 -*-
from flask import Flask, Response, render_template

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

    request = urllib.urlopen(uri)

    mimetype = request.headers.get('Content-Type', 'text/html')
    mimetype = mimetype.split(';')[0].strip()

    return Response(request.read(), status=request.getcode(),
                    mimetype=mimetype)

@app.route('/api/<path:path>')
def api_call(path):
    """
    """
    request = urllib.urlopen('%s/%s' % (app.config['SHIVA_URL'], path))

    return Response(request.read(), status=request.getcode(),
                    mimetype='application/javascript')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
