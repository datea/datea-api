###File Api

File uploads work with base64 data_uris (similar to images). 

Endpoints:

* /api/v2/file/
* /api/v2/file/\<id\>/

Allowed methods: GET, POST, PATCH, DELETE

####GET

user filters:
	
	user__id: <user id>,
	user__username: <username>,


####POST

	{
		file: {
    		data_uri: <data uri base64>,
    		name: 'somefilename.pdf'   			// pdf or kml supportes at the moment
    	}

    	order: 0 				// optional integer for ordering
	}