###Image Api

Image uploads work with base64 data_uris. This resource is thought to work in conjunction

Endpoints:
* /api/v2/image/
* /api/v2/image/\<id\>/

Allowed methods: GET, POST, PATCH, DELETE

####GET

user filters:
	
	user__id: <user id>,
	user__username: <username>,


####POST

	{
		image: {
    		data_uri: <data uri base64>,
    		name: 'somefilename.png'
    	}

    	order: 0 				// optional integer for ordering
	}



