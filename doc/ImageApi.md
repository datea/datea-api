###Image Endpoint

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

## Multipart Form Alternative to POST Image

Send a POST Request with an HTML form with appropriate auth headers or GET/POST params (see [Account Endpoint](AccountApi.md)) and the following parameters:

* image : the image file field
* order : optional integer to sort images.

You'll get back a json with the resource data.
