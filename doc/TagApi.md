###Tag Api

allowed methods = GET, POST, PATCH

Endpoints:

* List (Search): /api/v2/tag/
* Detail: /api/v2/tag/\<id\>/
* Schema: /api/v2/tag/schema/
* Autocomplete: /api/v2/tag/autocomplete/
* Trending: /api/v2/tag/trending/


####List and Search Tags

The following parameters may be given for the GET method:

* 'q': search for a phrase [string]
* 'trending_days': get the trending topics for the given last number of days [integer]
* 'trending_forever': If you provide this parameter, it will look for the most used tags since the beginnig (example: trending_forever=1. 


####Autocomplete suggestions

Issue a JSON GET request to */api/v2/tag/autocomplete/* with a 'q' param:

To autocomplete on "He":

	/api/v2/tag/atocomplete/?q=He

you'll receive a JSON with:

	{
		suggestions: ['Hello', 'Hey', 'Help']	
	}


###POST 

Params needed for POST to */api/v2/tag/* are:

	{
		tag 	: <tagname>, 		// required
		title 	: <a title>			// optional string with better description
	}
