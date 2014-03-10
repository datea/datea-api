###Follow Api

allowed methods = GET, POST, DELETE

Endpoints: 

* List: /api/v2/follow/
* Detail: /api/v2/follow/\<id\>/

Comments:
* Follow objects have a unique follow_key and user pairs. The database rejects double objects.  
* Follow objects have generic relations to other objects, which means, you can follow any other object of the API.
* "follow_key" is a convenience field to describe the object type and object id in one string. Example: 'tag.1000'.
* Follow objects always use the currently authenticated user. One can only create and delete follow objects for one's own user.

List follow filters:

* 'user__id': user id [int]
* 'follow_key': \<object type\>.\<id\> [String] (example: 'dateo.465' )

Number of results and pagingation:
* 'limit': number of results, defaults to 5 [int]
* 'offset': paging offset (e.g 5 for next page) [int]


POST:
	{
		follow_key: 'tag.1001',
	}

or (both are valid options)

	{
		content_type: 'tag',
		object_id: 1001
	}

