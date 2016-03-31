###Redateo Endpoint

A redateo is much like a retweet or reblog, but for dateos. It can put the original dateo in another user's feed, plus it includes the ability to add further tags, allowing the original dateo to appear in different maps/campaigns.

allowed methods = GET, POST, DELETE

Endpoints:

* List: /api/v2/redateo/
* Detail: /api/v2/redateo/\<id\>/
* Schema: /api/v2/redateo/schema/


####POST
Aplication/json POST to /api/v2/redateo

  {
    dateo : dateo id (int) or dateo object
  }

####DELETE
DELETE request to Detail endpoint.
