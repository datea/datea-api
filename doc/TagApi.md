###Tag Api

allowed methods = GET, POST, PATCH

Endpoints:

* List (Search): /api/v2/tag/
* Detail: /api/v2/tag/\<id\>/
* Schema: /api/v2/tag/schema/
* Autocomplete: /api/v2/tag/autocomplete/
* Trending: /api/v2/tag/trending/
* Nearby: /api/v2/tag/nearby/


####List and Search Tags

The following parameters may be given for the GET method:

* 'q': search for a phrase [string]

Number of results and pagingation:
* 'limit': number of results, defaults to 5 [int]
* 'offset': paging offset (e.g 5 for next page) [int]

orderby (prepend a '-' to invert):

* 'created' ('-created' for descending) 
* 'tag': order alphabeticaly


####Autocomplete suggestions

Issue a JSON GET request to */api/v2/tag/autocomplete/* with a 'q' param:

To autocomplete on "He":

	/api/v2/tag/atocomplete/?q=He

you'll receive a JSON with:

	{
		suggestions: ['Hello', 'Hey', 'Help']	
	}


####Trending tags

Endpoint: */api/v2/tag/trending/*

Filter parameters
* 'days': get the trending topics for the given last number of days [integer]
* 'forever': If you provide this parameter, it will look for the most used tags since the beginnig (forever=1)
* 'country': spelled mostly in their own language (e.g. Perú with tilde) [string]
* 'admin_level1': e.g. Region for Perú [string]
* 'admin_level2': e.g. Province  for Perú [string]
* 'admin_level3': e.g. District  for Perú [string]

Number of results and pagingation:
* 'limit': number of results, defaults to 5 [int]
* 'offset': paging offset (e.g 5 for next page) [int]

This endpoint caches the results for 10 minutes.


####Nearby

get nearby tags. Limited by default to 5 results

Endpoint: */api/v2/tag/nearby/*

Params:

* position: format is lat,lng (eg. -77.0842903555518717,-12.0090909568483948)
* limit: number of results [default 5, max 20]


###POST 

Params needed for POST to */api/v2/tag/* are:

	{
		tag 	: <tagname>, 		// required
		title 	: <a title>			// optional string with better description
	}
