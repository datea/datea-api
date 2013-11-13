# Sign-in with 3rd Party services

## Request from client
```json
{email: "",
 oauth_token: "",
 oauth_token_secret: ""}
```

## Response from server

```json
{
    secret: "xa7812egdsy"
}
```

Sucessive requests will include the secret on the HTTP Headars under the name of X-DATEA-AUTH

If unsucessful, return Http403


# Logout

invaldiate the headar


# Validating credentials from facebook

Pre-requiste: Having an access Token

Hit the following url: https://graph.facebook.com/debug_token?input_token={token_to_inspect}0&access_token={access_token}

```python
r = requests.get('https://graph.facebook.com/debug_token?input_token={token_to_inspect}0&access_token={access_token}'.format(
    token_to_inspect=unverified_token,
    access_token=access_token))
```

For more information see the [Facebook Documentation](https://developers.facebook.com/docs/facebook-login/manually-build-a-login-flow/#confirm)

# Getting an access token

Hit the following url: 'https://graph.facebook.com/oauth/access_token?client_id={app_id}&client_secret={client_secret}&grant_type=client_credentials'

```python
r = requests.get('https://graph.facebook.com/oauth/access_token?client_id={app_id}&client_secret={client_secret}&grant_type=client_credentials'.format(
    app_id=settings.FACEBOOK_KEY,
    app_secret=settings.FACEBOOK_SECRET))
```
For more information see the [Facebook Documentation](https://developers.facebook.com/docs/facebook-login/access-tokens/#apptokens)
