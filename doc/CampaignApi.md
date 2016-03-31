###Campaign Endpoint

allowed methods = GET, POST, PATCH, DELETE

Endpoints:

* List: /api/v2/campaign/
* Detail: /api/v2/campaign/\<id\>/
* Schema: /api/v2/campaign/schema/


####GET Params

Filters:
* q: search for a phrase
* user: filter by username [string]
* user_id: filter by user id [integer]
* published: [0, 1 or 'all'] (default is 1)
* id: object id
* main_tag: filter only by main tag (without hash) [string]
* main_tag_id: filter by main_tag id [integer]
* tags: comma separated tags (without hash) [strings]
* featured: boolean [0 or 1]

date related filters:
* created__year: year campaign was created [four digits] (watch for double underscore -> django filters)
* created__month: in combination with year, month campaign was created [two digits]
* created__day: combined with month and year, day a campaign was created [two digits]
* created__gt: created after date [date in ISO format]
* created__lt: created before date [date in ISO format]. Together with created__gt, you can form a range.

follow filters:
* followed_by_tags: get all campaigns by the tags a user follows. [user id: integer]

spatial filters:
* Within bounding box: 'bottom_left' and 'top_right' GET params need to be present (both) to filter campaigns which center is within a geographic bounding box. Each param has \<latitude,longitude\> [lat and long coordinates separated by commas -> "-95.23362278938293,38.973081081164715"]
* Within distance to point: 'distance' and 'center' GET params need to be present. Filters campaigns which center is within given distance in meters from given point. Center given as \<latitude,longitude\>, distance in meters as an integer.


######Order_options

The "order_by" GET parameter accepts a comma separated list of options. The first parameters take precedence.

example: order_by=score,-created

all parameters invert ascending or descending order when a '-' (minus) on front:

* 'created' -> created ascending
* '-created' -> descending (probably what you want)

options:
* 'score': works only in combination with 'q' parameter above, means search relevance
* 'created'
* 'published'
* 'dateo_count'
* 'comment_count'
* 'follow_count'
* 'distance': for dateos to be ordered by distance, you also need to specify a 'center' parameter, similar to the 'Within distance to point' filter above


####POST
Issue a Application/json POST request to /api/v2/campaign/ with:

	{
		name: <string>, 				// max 100 chars
		published: <boolean>,  			// 0 or 1
		end_date: <date in iso format>,	// (optional)
		short_description: <text>	  	// max 140 chars
		mission: <text>, 			  	// 500 chars
		information_destiny: <text>,  	// 500 chars

		category: <existing category resource> // check category endpoint

		main_tag: { 					// new or existing tag resource
			tag: "Jamsession",
			title: "longer title", 		optional
		},

		secondary_tags: [				// new or existing tag resources
			{
				tag: "Jamsession",
				title: "longer title",  // optional
			},
			...
		],

		image: {						// new or existing image resource
			image:	{
						data_uri: <data uri base64>,
						name: 'somefilename.png'
					},
			order: 0 				// optional integer for ordering
		}

		center: {						// geoJSON POINT
			type        : 'Point',
			coordinates : [ -77.027772, -12.121937 ],
		},

		boundary: {						// optional geoJSON POLYGON
			"type": "Polygon",
	         "coordinates": [
	           [ [100.0, 0.0], [101.0, 0.0], [101.0, 1.0],
	             [100.0, 1.0], [100.0, 0.0] ]
	           ]
		},

		layer_files: [						// optional new or existing File Resource objects (KML or geoJSON)
			{
				file:	{
						data_uri: <data uri base64>,
						name: 'somefilename.json'
					},
				order: 0 				// optional integer for ordering
			},
			...
		],
		default_vis: 'map'				// optional -> options are: 'map' (default), 'timeline', 'pictures', 'files'
		default_filter: 'owner'			// optional -> default is null

	}

	####PATCH, DELETE
	same as POST, but object has to include "id" and the request goes to the Detail url
