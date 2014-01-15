

###Account api:

400 ( Bad Request ):

* "Duplicate email"
* "Duplicate username"
* "Password too weak"
* "No user with that email"
* "oauth_token and oauth_token_secret not provided" (twitter)
* "access_token not provided" (facebook and other oauth2 clients)
* "Username cannot be empty"
* "Not a valid email address"

401 ( Unauthorized ):

* "Wrong username or password"
* "Account disabled"
* "Invalid reset link" (reset password)
* "Social access could not be verified"


404 ( Not found ):

* "User not found"  (reset password link)


200 ( OK ):

* "Check your email for further instructions"
* "Your password was successfully reset"






