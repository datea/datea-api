###Comment Endpoint

allowed methods = GET, POST, PATCH, DELETE

Endpoints:

* List: /api/v2/comment/
* Detail: /api/v2/comment/\<id\>/
* Schema: /api/v2/comment/schema/


####GET

Objects already come with related comments -> See Dateo.

List filters:

* user: user id [integer]
* content_type__model:  'dateo' [string]
* object_id: 123 [int]  

####POST
Application/json POST request to /api/v2/comment/ with:

	{
		comment: 'bla bla bla',
		object_id: 123,				// id of commented object
		content_type: 'dateo', 		// ctype of commented object
	}

the user is taken automatically from the current authenticated user.

####PATCH, DELETE
same as POST, but object has to include "id" and the request goes to the Detail url
