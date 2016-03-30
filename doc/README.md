###DATEA API ENDPOINT DOC

Here you can find a simple documentation of how to interact with the Datea API, useful for folks looking to contribute to the development of the Datea web and mobile clients, or if you'd like to do some experiment of your own. Feel free to contact us or file issues if any item in the doc is missing or does not work as stated.

The Datea API is designed to work 100% independently from the clients, which receive an api key or token after authentication which has to be included in the headers of all interactions with the API. GET operations are permitted without authentication in most cases though. Please protect the token of our users. The API currently works and has work on a https connection to avoid leaking user keys. Read more under the Account endpoint on how  to obtain a api_key for a user.

#Table of contents

[How to register a new client](RegisterAClient.md)
[Account endpoint](AccountApi.md)
[Campaign endpoint](CampaignApi.md)
[Comment endpoint](CommentApi.md)
[Dateo endpoint](DateoApi.md)
[Environment endpoint](EnvironmentApi.md)
[Extra endpoints](ExtraEndpoints.md)
[File endpoint](FileApi.md)
[Flag endpoint](FlagApi.md)
[Follow endpoint](FollowApi.md)
[Image endpoint](ImageApi.md)
[Messages endpoint](Messages.md)
[Notify endpoint](NotifyApi.md)
[Tag endpoint](TagApi.md)
[Vote endpoint](VoteApi.md)
