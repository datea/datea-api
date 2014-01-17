##Register a Client

The Datea Api provides an account system and a notifications system, that sends email to users in the following cases: 

* account activation through email when registering a Datea account
* password reset cycle
* confirming an email address
* Notifications for new dateos and comments (see NotificationsApi)

To link back or redirect to your client when users click on the links in the emails, you need to register a client with the API, providing those paths.

A registered client may provide:

* domain
* Site name / App name
* Register success redirect URL
* Register error redirect URL
* Change email success redirect URL
* Change email error redirect URL
* Password Reset Base Url, including parameters {uid} and {token}
* Dateo URL, that may include: {user_id}, {username}, {obj_id}
* Comment URL, that may include: {user_id}, {username}, {obj_id}, {comment_id}
* Notify Settings URL: in the email footer, for users who'd like to change their notification settings. Replacement params {user_id} and {username}

