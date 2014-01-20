###Notify Api


####Notify Settings

Notify settings come bundled in the user object, when you issue a GET request on a user endpoint with appropiate Authentication headers (username and apikey: see account api). They can also be saved independently.

allowed methods = GET, PATCH

Endpoint: */api/v2/notify_settings/\<id of notify settings objects\>/*

This object has a OneToOne relation with the User object. It defines which events trigger the system to send notification emails to the users of the plattform. 

Structure:

	{
		user: 			<user resource uri>, 		// readonly
		interaction: 	<boolean>,					// default: true
		conversations: 	<boolean>,					// default: true
    	tags_dateos: 	<boolean>,					// default: false
    	tags_reports: 	<boolean>,					// default: true
    	site_news: 		<boolean>,					// default: true
	} 

* interaction: send notifications when actions in the system occur that involve a users content. Eg a comment on my dateo, someone supported my dateo etc.
* conversations: send notifications when a new comment is created in a conversation a user participates. 
* tags_dateos: Send notofications when dateos occur in a tag a user follows
* tags_reports: Send notifications when reports by iniciatives are posted on a tag a user follows
* site_news: receive news letter.


####Notifications

allowed methods = GET, PATCH, DELETE

Endpoints:

* List: /api/v2/notification/
* Detail: /api/v2/notification/\<id\>/


Notification objects are created for users individually. Only the "unread" parameter can be changed with PATCH, in order to indicate that it was already read by the user. To do this, issue a PATCH with:

	{
		unread: false
	}

to the detail endpoint of a notification. 

At the moment, no list PATCH is allowed, only detail. This will probably change.

#####Notification content

Notification includes the following information:

	{
		type: <"dateo", "comment" or "vote">,
		recipient: <user resource uri>,
		unread: <boolean>,
		created: <date in iso format>,

		// json object containing info about the notification
		data: {		
			actor: <acting user username>,
			actor_id: <acting user id>,
			actor_img: <acting user thumb image>,
			action_object: <comment or dateo resource>  // (not necesary to have the vote object)
			verb: <"dateo", "commented", "voted">,	
			target_object: <full resource: dateo>,
			target_user: <target user username>,
			target_user_id: <target user userid>,
			target_object_name: <"dateo">,
			extract: <string extract of comment or dateo content>,	// 140 chars
		}
	}


*Filter params for GET list:*

* user: \<user id\>
* unread: 0 o 1 
* limit: \<number of results\>  (default: 7)
* offset: \<result offset\> [integer]


####ActivityLog (activity stream)

allowed methods = GET, PATCH

Endpoints:

* List: /api/v2/activity_log/
* Detail: /api/v2/activity_log/\<id\>/

The activitylog endpoint is meant to create activity streams. It provides two main modes: get activity around tags, and activity involving a user.

1. Tag activity

Get all activity around comma separated tags:

* tags: "oneTag,anotherTag"

2. User activity

There are different modes for user activity. Provide 2 params:

* user: \<user id\> [integer]
* mode: \<"actor","target_user","follow","all"\>

a. "actor" mode: get all activity in which the user is the actor (acting user)
b. "target_user": get all activity in which the user is the owner of the target objects
c. "follow": get all activity under the tags and conversations a user follows
d. "all": all of the above

This endpoint also has paginated output, providing the following parameters:

* limit: \<number of results\>  (default: 5)
* offset: \<result offset\> [integer]


#####activity Log content

	{
		id: 			<object id>
		created: 		<date in iso format>,
		actor:			<full acting user resource>,
	    verb:			<action type: "dateo", "voted", "commented">
	    action_object:	<full action resource: dateo, vote, comment>,
	    target_object:	<full target object: dateo>,	// optional
	    target_user: 	<full target user resource>, 	// optional
	    data: 			<extra data: extract etc>
	}




