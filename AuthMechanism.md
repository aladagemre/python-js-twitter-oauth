# Authentication Mechanism

In this post, I will be explaining the Twitter OAUTH Authentication mechanism and how I implemented it with javascript+python.
There are some unnecessary parts since I was inspired by satellizer. I didn't have chance to remove them completely.


## Frontend => Backend /auth/twitter

We've got a "Login with Twitter" link which 1) opens a blank popup window 2) starts a POST request to our backend /auth/twitter with payload:

    {u'name': u'twitter', u'url': u'/auth/twitter', u'popupOptions': {u'width': 495, u'height': 645}, u'authorizationEndpoint': u'https://api.twitter.com/oauth/authenticate', u'type': u'1.0', u'redirectUri': window.location.href}

which is evaluated as:

    {u'name': u'twitter', u'url': u'/auth/twitter', u'popupOptions': {u'width': 495, u'height': 645}, u'authorizationEndpoint': u'https://api.twitter.com/oauth/authenticate', u'type': u'1.0', u'redirectUri': u'http://127.0.0.1:9000'}


## Backend => Twitter /oauth/request_token

Backend receives this payload and sends a POST request to 'https://api.twitter.com/oauth/request_token' a payload containing  Oauth(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET, TWITTER_CALLBACK_URL).


## Twitter /oauth/request_token => Backend

Twitter responds this request with a payload:

    {
       "oauth_callback_confirmed": "true",
       "oauth_token": "..............",
       "oauth_token_secret": ".............."
    }

This means Twitter gave us a token and a token secret for initiating a new login. Twitter doesn't know anything about the user yet.

## Backend => Frontend

Now that oauth callback confirmed and Twitter's expecting someone to login, Backend responds Frontend with the previous payload.



## Popup => Twitter /oauth/authenticate

Frontend navigates the blank popup to the 'https://api.twitter.com/oauth/authenticate' with payload attributes as GET parameters. Twitter authorization page is displayed to the user. Use approves the authorization request.

## Popup Twitter => 302 => Popup CallbackURL (Backend)

After approval, Twitter redirects user to CallbackURL?oauth_token=x&oauth_verifier=y (our backend): localhost:9000/auth/twitter?oauth_token=x&oauth_verifier=y.

## CallbackURL (Backend) => Twitter /oauth/access_token

CallbackURL sees the user has approved the request. So with the oauth_token, oauth_verifier, Twitter Consumer Key and Twitter Consumer Secret; asks for profile details, access_token and access_token_secret from 'https://api.twitter.com/oauth/access_token'.

Twitter responds with profile details, access_token and access_token_secret.

## CallbackURL Backend => Popup Frontent

Backend generates a token using this data and renders templates/token.html containing a javascript code and generated token information. JS Code calls window.opener.setToken and window.opener.setScreenName methods.

Meanwhile, our frontend (main window) javascript code periodically check whether redirection came back to localhost. Since the redirection above results in our callback URL with token.html rendered, the check will succeed. It will close the popup window.

**TODO:** it may be possible that the window is closed before setToken method is fired.

## Frontend

Popup will fire setScreenName and setToken methods and these methods will write to localStorage and reflect the changes on the UI. Writing to HTTPS-Cookies could be a better idea. But for simplicity localStorage is a nice solution.
