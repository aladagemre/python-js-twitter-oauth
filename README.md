# README

## What is this project for?

This project aims to demo simplest version of Twitter Oauth login with pure Javascript (on the frontend) and Python (on the backend). Other solutions like satellizer forces you to use AngularJS. This project doesn't.

## Why did I code for this?

I could not find a simple way to do Twitter login with pure js. I had to use AngularJS to take advantage of satellizer. So I coded this.

## Installation

```bash
virtualenv --distribute venv
. venv/bin/activate
pip install -r requirements.txt
```

## Running

### Database

In another shell, at the same directory, start the mongodb database with:

```bash
mongod --dbpath=data
```

### Environment Variables

```bash
export TWITTER_CALLBACK_URL=http://127.0.0.1:9000/auth/twitter
export TWITTER_CONSUMER_KEY=...
export TWITTER_CONSUMER_SECRET=...
```

### Flask Web Server

```bash
python app.py
```

### Browse

Browse to http://127.0.0.1:9000

Press on Login, a popup will appear. Approve the Twitter login. Popup will close. You twitter handle and flask-generated token will appear on the page.


## Further Development

You can add new flask views with login_required decorator. This requires frontend to send token with each request.
