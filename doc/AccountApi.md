###Authentication

####Login
Ajax POST (application/json) to: /api/v2/account/login
with {username: <username>, password: <password}

you'll receive a:
* 200 if everything ok, with {token: <api_key>, 'userid': <int> }
* 401 if username or password is wrong
* 401 if account has been disabled

####Register
Ajax POST (application/json) to: /api/v2/account/register
with {username: <username>, email: <email>, password: <password>}

if everything ok, you'll receive:
* 201 message
* an email with instructions for activating the account will be sent to the user

otherwise you'll receive a 400 error:

* duplicate email: account with that email already exists
* duplicate user: there's an account with the same username


If your domain is whitelisted (contact us), then you may also additionally 
pass a "redirect_url": <activation_redirect_url>, specific for your app. Otherwise,
after clicking the activation link sent in the email, the user will be directed 
to a page from this system.


####Social Auth

Backends are facebook and twitter (possibly also google oauth2).

First, you need to authenticate with facebook or twitter from your client app. You can
do this by using our oauthd (from oauth.io) service like follows:

	<script src="http://api.datea.pe:6284/download/latest/oauth.js"></script>
	<script>
		OAuth.initialize('rT1wbk04eERCkSCMnA7vvdm5UcY');	// our public key may change in release
		
		/****** FACEBOOK ***********/

		//Using popup (option 1)
		OAuth.popup('facebook', function(error, result) {
  			//handle error with error
  			//use result.access_token in your API request
		});

		//Using redirection (option 2)	
		OAuth.redirect('facebook', "callback/url");

		/******* TWITTER **********/

		//Using popup (option 1)
		OAuth.popup('twitter', function(error, result) {
		  //handle error with error
		  //use result.oauth_token and result.oauth_token_secret in your API request
		});

		//Using redirection (option 2)
		OAuth.redirect('twitter', "callback/url");

	</script>

Then, for facebook auth with our api, issue a json ajax POST with:
	{'access_token': access_token}
to /api/v2/account/socialauth/facebook/

For twitter:, json ajax POST with:
	{oauth_token: oauth_token, oauth_token_secret: oauth_token_secret}
to /api/v2/account/socialauth/twitter/
  
If everything goes as expected, you'll receive a 200 with {token: api_key, 'userid': int }



####Reset Password
-> Tenemos que conversar sobre esto!
Ajax POST (application/json) to: /api/v2/account/reset_password