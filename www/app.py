# -*- coding: utf-8 -*-
from flask import Flask, Response, render_template
import requests

from shiva.www import config

app = Flask(__name__)
app.config.from_object(config)
app.static_folder = 'static'

@app.route('/')
def index():
    response = requests.get('%s/%s' % (app.config['NODEJS_URL'], path))

    return Response(response=response.content, status=response.status_code,
                    headers=response.headers)

@app.route('/api/<path:path>')
def api_call(path):
    """
    """
    response = requests.get('%s/%s' % (app.config['SHIVA_URL'], path))

    return Response(response=response.content, status=response.status_code,
                    headers=response.headers)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
