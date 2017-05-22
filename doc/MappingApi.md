###Mapping Endpoint

The mapping endpoint combines Tags and Campaigns into one Endpoint. Only Tags that are not part of a Campaign are shown, which makes it easier to search and display maps of relevance in Datea.

allowed methods = GET

Endpoints:

* List: /api/v2/mapping/

####GET Params

Filters:
* q: search for a phrase
* user: filter by username [string]
* user_id: filter by user id [integer]
* published: [0, 1 or 'all'] (default is 1)  (\*)
* id: object id

date related filters:
* created__year: year campaign/tag was created [four digits] (watch for double underscore -> django filters)
* created__month: in combination with year, month campaign/tag was created [two digits]
* created__day: combined with month and year, day a campaign/tag was created [two digits]
* created__gt: created after date [date in ISO format]
* created__lt: created before date [date in ISO format]. Together with created__gt, you can form a range.

follow filters:
* followed_by_tags: get all campaigns/tags a user follows. [user id: integer]

spatial filters (only applies to campaigns):
* Within bounding box: 'bottom_left' and 'top_right' GET params need to be present (both) to filter campaigns which center is within a geographic bounding box. Each param has \<latitude,longitude\> [lat and long coordinates separated by commas -> "-95.23362278938293,38.973081081164715"]
* Within distance to point: 'distance' and 'center' GET params need to be present. Filters campaigns Which center is within given distance in meters from given point. Center given as \<latitude,longitude\>, distance in meters as an integer.


######Order_options

The "order_by" GET parameter accepts a comma separated list of options. The first parameters take precedence. Default is '-rank', which is an internal value computed by the number of dateos and other values weighted according to time, in order to allow for "trending" campaigns/tags to surface at the front.
When doing a keyword search (including the "q" filter), the default switches to "score,-rank". "score" is the search engine's parameter for search relevance.

example: order_by=-rank,-created

all parameters invert ascending or descending order with a '-' (minus) on front:

* 'created' -> created ascending
* '-created' -> descending (probably what you want)

options:
* 'score': works only in combination with 'q' parameter above, means search relevance
* 'created'
* 'published'
* 'dateo_count'
* 'follow_count'
* 'distance': for campaigns (only to be ordered by distance, you also need to specify a 'center' parameter, similar to the 'Within distance to point' filter above


####Mapping autocomplete

allowed methods = GET

Endpoints:

* List: /api/v2/mapping/autocomplete

####GET Params

Filters:
* q: search for a phrase
* limit: num of results [int], default 10
