###Dateo Api

allowed methods = GET, POST, PATCH, DELETE

Endpoints:

* List: /api/v2/dateo/
* Detail: /api/v2/dateo/\<id\>/
* Schema: /api/v2/dateo/schema/


####GET Params


Filters:
* q: search for a phrase
* user: filter by username [string]
* user_id: filter by user id [integer]
* status: filter by status ['new', 'reviewed', 'solved']
* published: [boolean: 0 or 1]
* show_unpublished: also show unpublished dateos. Only for one's own dateos, used in combination with user_id [boolean: 0 or 1]
* id: object id
* tags: comma separated tags (without hash) [strings]

Number of results and pagingation:
* 'limit': number of results, defaults to 100 [int]
* 'offset': paging offset (e.g 100 for next page) [int]

date related filters:
* created__year: year dateo was created [four digits] (watch for double underscore -> django filters)
* created__month: in combination with year, month dateo was created [two digits]
* created__day: combined with month and year, day a dateo was created [two digits]
* created__gt: created after date [date in ISO format]
* created__lt: created before date [date in ISO format]. Together with created__gt, you can form a range.

follow filters:
* followed_by_tags: get all dateos by the tags a user follows. [user id: integer]
* followed: get all dateos followed individually (because of comment system) [user id: integer]

political filters:
At the moment we have fields for 3 administrative levels besides 'Country'. In Perú this means: Regions, Provinces, Districts. We're looking forward to provide a service like mapit by mysociety, in order to fill this fields automatically, but you can use that service or other service at client level.

* country: spelled mostly in their own language [string]
* admin_level1: Region (Perú) [string]
* admin_level2: Province (Perú) [string]
* admin_level3: District (Perú) [string]

spatial filters:
* Within bounding box: 'bottom_left' and 'top_right' GET params need to be present (both) to filter dateos by a geographic bounding box. Each param has \<latitude,longitude\> [lat and long coordinates separated by commas -> "-95.23362278938293,38.973081081164715"]
* Within distance to point: 'distance' and 'position' GET params need to be present. Filters dateos within given distance in meters from given point. Position given as \<latitude,longitude\>, distance in meters as an integer.


######Order_options

The "order_by" GET parameter accepts a comma separated list of options. The first parameters take presedence.

example: order_by=score,-created

all parameters invert ascending or descending order when a '-' (minus) on front:

* 'created' -> created ascending
* '-created' -> descending (probably what you want)

options: 
* 'score': works only in combination with 'q' parameter above, means search relevance
* 'created'
* 'published'
* 'comment_count'
* 'vote_count'
* 'date' -> for dateos that specify a date other than created
* 'address' -> alphabetically per address field
* 'distance': for dateos to be ordered by distance, you also need to specify a 'position' parameter, similar to the 'Within distance to point' filter above


####POST

	{
		  address:	'Calle x 546',			  	// (optional)
    	category:	'/api/v2/category/1/',  	// category resource_uri (optional)
    	content:	'this is a test';
    	position: 	{ 					  		// (optional)
    					coordinates : [ -77.027772, -12.121937 ], 
        				type        : 'Point',
    				},
    	tags: 		[ { tag : 'testTag' },
        	    	  { tag : 'Aaaa', 		  	// existing tag
            	  		title: 'aaaa',
              			dateo_count  : 10,
              			description  : '',
              			follow_count : 0,
             			id           : 3,
              			resource_uri : '/api/v2/tag/3/',
            	  		}
           			],
    	date:   	<date in ISO format>,		// (optional)
    	images:		[{
    					image:	{
    								data_uri: <data uri base64>,
    								name: 'somefilename.png'
    							}
    					order: 0 				// optional integer for ordering

    				}]
	}
