# -*- coding: utf-8 -*-
from flask import redirect, render_template, request, session
from flask_oauthlib.provider import OAuth1Provider

from shiva.models import AccessToken, Client, Nonce, RequestToken
from shiva.http import JSONResponse


# Code copied from http://lepture.com/en/2013/create-oauth-server
def register(app):
    """ Registers the app as an OAuth provider. """

    oauth = OAuth1Provider(app)

    def current_user():
        if 'id' in session:
            uid = session['id']
            return User.query.get(uid)

        return None

    @app.before_request
    def auth():
        # TODO: Close everything to authenticated users only, unless otherwise
        # specified. Use the settings ALLOW_ANONYMOUS_ACCESS for that.
        if not app.config.get('ALLOW_ANONYMOUS_ACCESS'):
            client_key = request.values.get('client_key')

            if not client_key:
                return JSONResponse(401)

            # TODO: How do you check if the user was authorized already or not?
            # client = Client.query.get(client_key)
            if Client.query.filter_by(key=client_key).count() == 0:
                return JSONResponse(401)

    @oauth.clientgetter
    def load_client(key):
        return Client.query.get(key)

    @oauth.clientgetter
    def load_client(key):
        return Client.query.get(key)

    @oauth.grantgetter
    def load_request_token(token):
        return RequestToken.query.filter_by(token=token).first()

    @oauth.grantsetter
    def save_request_token(token, request):
        if hasattr(oauth, 'realms') and oauth.realms:
            realms = ' '.join(request.realms)
        else:
            realms = None
        grant = RequestToken(
            token=token['oauth_token'],
            secret=token['oauth_token_secret'],
            client=request.client,
            redirect_uri=request.redirect_uri,
            _realms=realms,
        )
        db.session.add(grant)
        db.session.commit()
        return grant

    @oauth.verifiergetter
    def load_verifier(verifier, token):
        return RequestToken.query.filter_by(
            verifier=verifier, token=token
        ).first()

    @oauth.verifiersetter
    def save_verifier(token, verifier, *args, **kwargs):
        tok = RequestToken.query.filter_by(token=token).first()
        tok.verifier = verifier['oauth_verifier']
        tok.user = current_user()
        db.session.add(tok)
        db.session.commit()

        return tok

    @oauth.noncegetter
    def load_nonce(client_key, timestamp, nonce, request_token, access_token):
        params = {
            'access_token': access_token,
            'client_key': client_key,
            'nonce': nonce,
            'request_token': request_token,
            'timestamp': timestamp,
        }

        return Nonce.query.filter_by(**params).first()

    @oauth.noncesetter
    def save_nonce(client_key, timestamp, nonce, request_token, access_token):
        params = {
            'access_token': access_token,
            'client_key': client_key,
            'nonce': nonce,
            'request_token': request_token,
            'timestamp': timestamp,
        }

        nonce = Nonce(**params)
        db.session.add(nonce)
        db.session.commit()

        return nonce

    @oauth.tokengetter
    def load_access_token(client_key, token, *args, **kwargs):
        return AccessToken.query.filter_by(client_key=client_key,
                                           token=token).first()

    @oauth.tokensetter
    def save_access_token(token, request):
        tok = AccessToken(client=request.client, user=request.user,
                          token=token['oauth_token'],
                          secret=token['oauth_token_secret'],
                          _realms=token['oauth_authorized_realms'])
        db.session.add(tok)
        db.session.commit()

    @app.route('/oauth/request_token')
    @oauth.request_token_handler
    def request_token():
        return {}

    @app.route('/oauth/access_token')
    @oauth.access_token_handler
    def access_token():
        return {}

    @app.route('/oauth/authorize', methods=['GET', 'POST'])
    @oauth.authorize_handler
    def authorize(*args, **kwargs):
        user = current_user()

        if not user:
            return redirect('/')

        if request.method == 'GET':
            client_key = kwargs.get('resource_owner_key')
            client = Client.query.filter_by(key=client_key).first()
            kwargs['client'] = client
            kwargs['user'] = user

            return render_template('authorize.html', **kwargs)

        confirm = request.form.get('confirm', 'no')

        return confirm == 'yes'

    @app.route('/api/me')
    @oauth.require_oauth()
    def me():
        user = request.user

        return jsonify(username=user.username)
