import os
import jwt
import json
import base64
import requests
from functools import wraps
from urlparse import parse_qsl
from requests_oauthlib import OAuth1
from mongoengine import DoesNotExist
from datetime import datetime, timedelta
from jwt import DecodeError, ExpiredSignature
from flask.ext.mongoengine import MongoEngine
from flask import Flask, g, send_file, request, jsonify, render_template


current_path = os.path.dirname(__file__)
client_path = os.path.abspath(os.path.join(current_path, 'frontend'))

app = Flask(__name__, static_url_path='', static_folder=client_path)
app.config.from_object('config')

db = MongoEngine(app)

class TwitterAccount(db.EmbeddedDocument):
    user_id = db.StringField(required=True, max_length=100)
    screen_name = db.StringField(max_length=100)
    oauth_token = db.StringField(max_length=100)
    oauth_token_secret = db.StringField(max_length=100)
    x_auth_expires = db.StringField(max_length=100)
    timestamp = db.DateTimeField()
    active = db.BooleanField(default=True)

class User(db.Document):
    email = db.StringField(max_length=100)
    display_name = db.StringField(max_length=100)
    twitter = db.EmbeddedDocumentField(TwitterAccount)
    active = db.BooleanField(default=True)

    def to_json(self):
        def ion(provider):
            """
            If there exists an account and it is active ,returns userid.
            Otherwise, returns None.
            :param provider:
            :return:
            """
            provider_account = getattr(self, provider)
            userid = None
            if provider_account and provider_account.active:
                userid = getattr(provider_account, "user_id")
            return userid

        return dict(id=str(self.id),
                    email=self.email,
                    displayName=self.display_name,
                    twitter=ion('twitter'))


def get_user_from_db(provider, profile):
    providerid = profile.get("user_id")
    try:
        u = User.objects(**{"%s__%s" % (provider, "user_id"): providerid,
                            "%s__%s" % (provider, "active"): True}).get()
        return u
    except DoesNotExist, e:
        return None

def create_token(user):
    payload = {
        'sub': str(user.id),
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(days=14)
    }
    token = jwt.encode(payload, app.config['TOKEN_SECRET'])
    return token.decode('unicode_escape')


def parse_token(req):
    token = req.headers.get('Authorization').split()[1]
    return jwt.decode(token, app.config['TOKEN_SECRET'])


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.headers.get('Authorization'):
            response = jsonify(message='Missing authorization header')
            response.status_code = 401
            return response

        try:
            payload = parse_token(request)
        except DecodeError:
            response = jsonify(message='Token is invalid')
            response.status_code = 401
            return response
        except ExpiredSignature:
            response = jsonify(message='Token has expired')
            response.status_code = 401
            return response

        g.userid = payload['sub']

        return f(*args, **kwargs)

    return decorated_function

@app.route('/')
def index():
    return send_file(os.path.join(client_path, 'index.html'))

@app.route('/api/me')
@login_required
def me():
    user = User.objects.get_or_404(id=g.userid)
    return jsonify(user.to_json())

def process_provider(provider, profile, request):
    providerid_field = "user_id"

    # If user exists, return the token so that they can login.
    user = get_user_from_db(provider, profile)
    if user:
        token = create_token(user)
        return token

    # If the social user does not exist in the database,
    # Get userid from the response from provider
    try:
        # check if are already logged. if so, get the account: u.
        payload = parse_token(request)
        userid = payload.get('sub')
        # todo: sub is used for mongo user_id. confusing.
        u = User.objects.get_or_404(id=userid)
        if not u.display_name:
            u.display_name = profile.get('screen_name')
    except:
        # if we are not logged, create a new user: u.
        name = profile.get('screen_name')
        u = User(display_name=name)

    # whether u is a new or existing user, connect social account.
    social_account = TwitterAccount(**profile)
    setattr(u, provider, social_account)
    u.save()

    token = create_token(u)
    return token



@app.route('/auth/twitter', methods=['GET','POST'])
def twitter():
    request_token_url = 'https://api.twitter.com/oauth/request_token'
    access_token_url = 'https://api.twitter.com/oauth/access_token'
    args = request.json or request.args

    if args.get(u'oauth_token') and args.get(u'oauth_verifier'):
        # second step
        auth = OAuth1(app.config['TWITTER_CONSUMER_KEY'],
                      client_secret=app.config['TWITTER_CONSUMER_SECRET'],
                      resource_owner_key=args.get('oauth_token'),
                      verifier=args.get('oauth_verifier'))
        r = requests.post(access_token_url, auth=auth)
        profile = dict(parse_qsl(r.text))

        token = process_provider("twitter", profile, request)
        return render_template('token.html', token=token, screen_name=profile.get('screen_name'))
    else:
        # Initial step
        oauth = OAuth1(app.config['TWITTER_CONSUMER_KEY'],
                       client_secret=app.config['TWITTER_CONSUMER_SECRET'],
                       callback_uri=app.config['TWITTER_CALLBACK_URL'])
        r = requests.post(request_token_url, auth=oauth)
        oauth_token = dict(parse_qsl(r.text))
        return jsonify(oauth_token)



@app.route('/auth/unlink/', methods=['POST'])
@login_required
def unlink():
    print g.userid
    provider = request.json.get('provider')
    user = User.objects.get_or_404(id=g.userid)
    pa = getattr(user, provider)
    pa.active = False
    pa.save()
    return jsonify(user.to_json())



if __name__ == '__main__':
    app.run(port=9000)
