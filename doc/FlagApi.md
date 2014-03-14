###Flag Api

- flag inappropiate content (or flag it for other reasons
- takes always logged in user as the user for the flag when posting

allowed methods = GET, POST, DELETE

Endpoints: 

* List: /api/v2/flag/
* Detail: /api/v2/flag/\<id\>/

POST

	{
		content_type: 'comment',  // 'dateo', 'comment' or 'campaign'
		object_id: 1001,
		comment: 'I flagged this because of bla bla'
	}



