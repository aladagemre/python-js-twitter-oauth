import os

DEBUG = True

TOKEN_SECRET = os.environ.get('SECRET_KEY') or 'JWT Token Secret String'
TWITTER_CONSUMER_KEY = os.environ.get('TWITTER_CONSUMER_KEY') or 'Twitter Consumer Secret'
TWITTER_CONSUMER_SECRET = os.environ.get('TWITTER_CONSUMER_SECRET') or 'Twitter Consumer Secret'
TWITTER_CALLBACK_URL = os.environ.get('TWITTER_CALLBACK_URL') or 'Twitter Redirect URI'
