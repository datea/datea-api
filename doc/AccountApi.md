###Authentication Api

####Login
Ajax POST (application/json) to: */api/v2/account/login/*
with 

	{
		username: <username>, 
		password: <password>
	}

you'll receive a:
* 200 if everything ok, with 

	{
		token: <api_key>, 
		user: <user object> 
	}

* 401 if username or password is wrong
* 401 if account has been disabled

####Register
Ajax POST (application/json) to: */api/v2/account/register/*
with 

	{
		username: <username>, 
		email: <email>, 
		password: <password>
	}

if everything ok, you'll receive:
* 201 message
* an email with instructions for activating the account will be sent to the user

otherwise you'll receive a 400 error:

* duplicate email: account with that email already exists
* duplicate user: there's an account with the same username


If your domain is whitelisted (contact us), then you may also additionally 
pass the following parameters specific for your app:

	{
		...
		success_redirect_url: <url>,
		error_redirect_url: <url>
	}

Otherwise, after clicking the activation link sent in the email, the user will be directed 
to a page from this system.


####Social Auth

Backends are facebook and twitter (possibly also google oauth2).

First, you need to authenticate with facebook or twitter from your client app. You can
do this by using our oauthd (from oauth.io) service like follows:

	<script src="http://api.datea.pe:6284/download/latest/oauth.js"></script>
	<script>
		OAuth.initialize('rT1wbk04eERCkSCMnA7vvdm5UcY');	// our public key may change on release time
		
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

Then, for facebook auth with our api, issue a json ajax POST to */api/v2/account/socialauth/facebook/*
	
	{
		access_token: <access_token>
	}

For twitter:, json ajax POST to */api/v2/account/socialauth/twitter/* with
	
	{
		oauth_token: <oauth_token>, 
		oauth_token_secret: <oauth_token_secret>
	}

  
If everything goes as expected, you'll receive a 200 with: 
	
	{
		token: <api_key>, 
		user: <user_object>, 
		is_new: <boolean> 
	}


If you authenticate via twitter, the user will start with a 'status': 0 (unconfirmed) parameter, because twitter doesn't provide email addresses. To use this system, the user has to confirm his/her email address first, which brings us to:

####Changing email

When the email address of a user is changed and sent in a PATCH (no PUT allowed, see User resource below) request to the user endpoint:

* the new email address is saved
* user's status field is set to 0 (unconfirmed)
* an email will be sent to the new email address to confirm it

If you'd like the API to redirect back to your page when the user clicks the activation link sent to him/her, you need to white list your domain with us and also provide the following additional parameters in the user object:
	
	{
		...
		success_redirect_url: <url>
		error_redirect_url: <url>
	}


####Reset Password

Ajax POST (application/json) to: */api/v2/account/reset-password/* with:
	
	{
		email: <email>
	}

This will send a message to the given address with instructions - a link to access the password reset form. If you'd like the link in the email to redirect to a password reset form in your page, whitelist your domain with us, and add:
	
	{
		...
		base_url: <url to handle password reset>,
	}

otherwise it will be handled by system views.

The url contains is build like this:

	[base_url]/[uid]/[token]/


#### Reset Password confirm

if your domain is whitelisted, and you sent the "base_url" parameter in the previous step, you'll need to 
confirm the password reset. Have the user enter his/her new password twice, check if both fields against each other, and then:

Send a Ajax JSON POST to : */api/v2/account/reset-password-confirm/* with
	
	{
		password: <new password entered by user>,
		uid: <uid from reset url>,
		token: <token from reset url>
	}

if everything ok, you'll get a 200


###Authentication

For POST,PUT,PATCH and DELETE methods api wide, you need to authenticate the user. This is done using the provided api_key and the username you get from the methods above. You have two options:
	
	# As a header
	# Format is ``Authorization: ApiKey <username>:<api_key>
	Authorization: ApiKey daniel:204db7bcfafb2deb7506b89eb3b9b715b09905c8

	# As GET params
	http://api.datea.pe/api/v2/entries/?username=daniel&api_key=204db7bcfafb2deb7506b89eb3b9b715b09905c8


###User Api

allowed methods = GET, PATCH, DELETE

Users are created with the account api above, so no POST method here.

Endpoints:

* List: /api/v2/user/
* Detail: /api/v2/user/\<id\>/
* Detail (alternative): /api/v2/user/\<username\>/
* Schema: /api/v2/user/schema/

####GET

Example User Object:

	{
		username: 'fulanito',
		fullname: 'Fulano Menganez',
		id: <int>,
		image: <path to medium sized image>,    // paths are relative to the API domain (api.datea.pe)
		image_large: <path to large image>,		// See patch example on how to save image
		image_small: <path to small image>,
		date_joined: "2013-12-23T12:15:04.800938",  // date in ISO format. Read only field.
		last_login: "2013-03-02T03:23:22.247000",	// Read only field
		message: <a personal message, status text>,
		resource_uri: '/api/v2/user/<id>/',
		dateo_count: <int>,						// how many dateos he/she has made
		comment_count: <int>,
		vote_count: <int>,
		status: <0, 1, or 2>	// 0->unconfirmed, 1->confirmed, 2->banned.
								// Status field is only visible for one's own user when authenticated
	}

####PATCH

An example. Other fields are ignored. As with PATCH, you need only to provide the fields you want to change, and of course, the id.
	
	{
		id: <userid>
		username: <username>,
		fullname: <fullname>,	
		message: <message>,
		email: <valid email address>,
		image: {
			image:	{
    			data_uri: <data uri base64>,
    			name: 'somefilename.png'
    		}
		}
	}

