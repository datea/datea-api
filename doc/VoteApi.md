###Vote Api

allowed methods = GET, POST, DELETE

Endpoints: 

* List: /api/v2/vote/
* Detail: /api/v2/vote/\<id\>/

Comments:
* Vote objects have a unique vote_key and user pairs. The database rejects double objects.  
* Vote objects have generic relations to other objects, which means, you can vote on any other object of the API.
* "vote_key" is a convenience field to describe the object type and object id in one string. Example: 'dateo.1000'.
* Vote objects always use the currently authenticated user. One can only create and delete vote objects for one's own user.

*GET filters:*

* 'user__id': user id [int]
* 'vote_key': \<object type\>.\<id\> [String] (example: 'dateo.465' )
* 'content_type': \<object name>\  [String] (example: 'dateo')
* 'object_id': \<id\> [int]

Number of results and pagingation:
* 'limit': number of results, defaults to 5 [int]
* 'offset': paging offset (e.g 5 for next page) [int]


*POST:*
	{
		vote_key: 'tag.1001',
	}

or (both are valid options)

	{
		content_type: 'tag',
		object_id: 1001
	}


*DELETE:*

You can only delete vote objects that belong to your user. You need to send the api key and user name in the header, as described in AccountApi. There are 3 ways to delete vote objects. Examples:

1. Issue a DELETE request to /api/v2/vote/366/

2. DELETE request to /api/v2/vote/?user=\<user id\>&content_type=tag&object_id=366

3. DELETE request to /api/v2/vote/?user=\<user id\>&vote_key=tag.366
