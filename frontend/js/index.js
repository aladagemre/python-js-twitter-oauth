window.setToken = function (token, screen_name) {
  console.log('Setting token:', token)
  console.log('Setting screen_name:', screen_name)
  localStorage.setItem('token', token)
  localStorage.setItem('screen_name', screen_name)
  setCredentials(token, screen_name)
}

function setCredentials(token, screen_name){
  var span_screen_name = document.getElementById('screen_name')
  var span_token = document.getElementById('token')
  var span_status = document.getElementById('status')

  var loggedin = (token && screen_name)
  span_screen_name.innerHTML = screen_name
  span_token.innerHTML = token
  span_status.innerHTML = loggedin ? "Logged in" : "Not logged in"
}

function logout () {
  setCredentials("", "")
}

window.onload = function () {
  var token = localStorage.getItem('token')
  var screen_name = localStorage.getItem('screen_name')
  console.log(token)
  setCredentials(token, screen_name)
}

function login () {
  var defaults = {
    name: 'twitter',
    url: '/auth/twitter',
    authorizationEndpoint: 'https://api.twitter.com/oauth/authenticate',
    redirectUri: window.location.origin,
    type: '1.0',
    popupOptions: { width: 495, height: 645 }
  }
  var myWindow = window.open('_blank', 'twitter login', 'menubar=no,toolbar=no,resizable=yes,scrollbars=yes,height=495,width=645');
  fetch('/auth/twitter', {
  	method: 'POST',
  	mode: 'cors',
  	redirect: 'follow',
    body: JSON.stringify(defaults),
    data: JSON.stringify(defaults),
    json: JSON.stringify(defaults),
  	headers: new Headers({
  		'Content-Type': 'application/json'
  	})
  }).then(function(response) {
      return response.json()
   }).then(function(j){
     data = j
     var qs = 'oauth_callback_confirmed=' + data['oauth_callback_confirmed'] + '&oauth_token=' + data['oauth_token'] + '&oauth_token_secret=' + data['oauth_token_secret']
    myWindow.location.href = defaults.authorizationEndpoint + '?' + qs
    var timer = setInterval(checkURL, 1000)
    function checkURL () {
      // TODO: what if we check before document load?
      try {
        var url = myWindow.location.href
        if (url.indexOf(defaults.redirectUri) != -1){
          console.log('Auth complete!')
          clearInterval(timer);
          myWindow.close()
        }
      }
      catch(e) {}
    }
    console.log(j)
  })
}
