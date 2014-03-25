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

*GET filters:*

* 'user__id': user id [int]
* 'follow_key': \<object type\>.\<id\> [String] (example: 'tag.465' )
* 'content_type': \<object name>\  [String] (example: 'tag')
* 'object_id': \<id\> [int]

Number of results and pagingation:
* 'limit': number of results, defaults to 5 [int]
* 'offset': paging offset (e.g 5 for next page) [int]


*POST:*
	{
		follow_key: 'tag.1001',
	}

or (both are valid options)

	{
		content_type: 'tag',
		object_id: 1001
	}


*DELETE:*

You can only delete follow objects that belong to your user. You need to send the api key and user name in the header, as described in AccounApi. in There are 3 ways to delete follow objects. Examples:

1. Issue a DELETE request to /api/v2/follow/366/

2. DELETE request to /api/v2/follow/?user=\<user id\>&content_type=tag&object_id=366

3. DELETE request to /api/v2/follow/?user=\<user id\>&follow_key=tag.366



