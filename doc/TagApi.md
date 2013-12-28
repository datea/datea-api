###Dateo Api

allowed methods = GET, POST, PATCH, DELETE

Endpoints:

List: /api/v2/tag/
Detail: /api/v2/tag/<id>/
Schema: /api/v2/tag/schema/
Autocomplete: /api/v2/tag/autocomplete/



####Autocomplete suggestions

Issue a JSON GET request to /api/v2/tag/autocomplete/ with a 'q' param:

To atocomplete on "He":

	/api/v2/tag/atocomplete/?q=He

you'll receive a JSON with:

	{	suggestions: ['Hello', 'Hey', 'Help']	}


###POST 

Params needed for post to /api/v2/tag/ are:
	{
		tag 	: <tagname>, 		// required
		title 	: <a title>			// optional string with better description
	}
