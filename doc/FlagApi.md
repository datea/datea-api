###Flag Endpoint

- flag inappropiate content (or flag it for other reasons
- takes always logged in user as the user for the flag when posting

allowed methods = GET, POST, DELETE

Endpoints:

* List: /api/v2/flag/
* Detail: /api/v2/flag/\<id\>/

####POST
Application/json POST request to /api/v2/flag/ with:

	{
		content_type: 'comment',  // Options are 'dateo', 'comment' or 'campaign'
		object_id: 1001, // int
		comment: 'I flagged this because of bla bla'
	}


####DELETE
send DELETE request to the Detail url. Object has to include "id".
