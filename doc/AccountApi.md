###Authentication

####Login
Ajax POST (application/json) to: /api/v2/account/login
with {username: <username>, password: <password}

you'll receive a:
* 200 if everything ok
* 401 if username or password is wrong
* 401 if account has been disabled

####Register
Ajax POST (application/json) to: /api/v2/account/register
with {username: <username>, email: <email>, password: <password>}

if everything ok, you'll receive:
* 201 message
* an email with instructions for activating the account

otherwise you'll receive a 400 error:

* duplicate email: account with that email already exists
* duplicate user: there's an account with the same username
  
####Activate
Ver como hacemos en este caso, porque manda un correo con el codigo de activacion.

to activate the account, POST to: /api/v2/account/activate
with {activation_key: <activation_key>}

you'll receive a: 
* 200 if everything ok
* 401 if key has expired


####Reset Password
-> Tenemos que conversar sobre esto!
Ajax POST (application/json) to: /api/v2/account/reset_password