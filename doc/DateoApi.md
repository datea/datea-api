###Dateo Api

allowed methods = GET, POST, PUT, PATCH, DELETE

Endpoints:

List: /api/v2/dateo/
Detail: /api/v2/dateo/<id>/
Schema: /api/v2/dateo/schema/


####GET Params

* q: search for a phrase
* user: filter by username [string]
* user_id: filter by user id [integer]
* status: filter by status ['new', 'reviewed', 'solved']
* published: [boolean: 0 or 1]
* show_unpublished: also show unpublished dateos. Only for one's own dateos, used in combination with user_id [boolean: 0 or 1]

date related:
* created__year: year dateo was created [four digits] (watch for double underscore -> django filters)
* created__month: in combination with year, month dateo was created [two digits]
* created__day: combined with month and year, day a dateo was created [two digits]
* created__gt: created after date [date in ISO format]
* created__lt: created before date [date in ISO format]. Together with created__gt, you can form a range.
* followed_by_tags: get all dateos by the tags a user follows. [user id: integer]
* followed: get all dateo followed individually (because of comment system) [user id: integer]

spatial search params:

* Within bounding box: 'bottom_left' and 'top_right' GET params need to be present (both) to filter dateos by a geographic bounding box. Each param has <latitude,longitude> [lat and long coordinates separated by commas -> "-95.23362278938293,38.973081081164715"]
* Within distance to point: 'distance' and 'position' GET params need to be present. Filters dateos within given distance in meters from given point. Position given as <latitude,longitude>, distance in meters as an integer.


######Order_options

The "order_by" GET parameter accepts a comma separated list of options. The first parameters take presedence.

example: order_by=score,-created

all parameters invert ascending or descending order when a '-' (minus) on front:

'created' -> created ascending
'-created' -> descending (probably what you want)

options: 
* 'score': works only in combination with 'q' parameter above, means search relevance
* 'created'
* 'published'
* 'comment_count'
* 'vote_count'
* 'date' -> for dateos that specify a date other than created
* 'address' -> alphabetically per address field
* 'distance': for dateos to be ordered by distance, you also need to specify a 'position' parameter, similar to the 'Within distance to point' filter above


