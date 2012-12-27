# -*- coding: utf-8 -*-
from flask import Flask, Response, render_template
import requests

app = Flask(__name__)
app.static_folder = 'static'

@app.route('/')
def index():
    return render_template('shiva.html')

@app.route('/api/<path:path>')
def api_call(path):
    """
    """
    r = requests.get('http://localhost:5000/%s' % path)

    return Response(response=r.content, status=r.status_code,
                    headers=r.headers)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
