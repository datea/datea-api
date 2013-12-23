datea-api
=========


Api Usage
---------


###Authentication

####Login
Ajax POST (application/json) to: /api/v2/account/login
with {username: <username>, password: <password}


####Register
Ajax POST (application/json) to: /api/v2/account/register
with {username: <username>, email: <email>, password: <password>}

if everything ok, you'll receive an email with instructions for activating the account

otherwise you'll receive a 400 error:
  
  
