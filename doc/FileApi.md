###File Endpoint

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
Application/json POST request to /api/v2/file/ with:

	{
		file: {
  		data_uri: <data uri base64>,
  		name: 'somefilename.pdf'  // pdf or kml supportes at the moment
  	}
		title : 'some title' // optional specify a title/name for the file
    order : 0 				// optional integer for ordering
	}

#### Multipart Form Alternative to POST File

Send a POST Request with an HTML form with appropriate auth headers or GET/POST params (see [Account Endpoint](AccountApi.md)) and the following parameters:

* image : the file field
* title : optional title for the file
* order : optional integer to sort images.

You'll get back a json with the resource data.

####PATCH, DELETE
same as POST, but object has to include "id" and the request goes to the Detail url
