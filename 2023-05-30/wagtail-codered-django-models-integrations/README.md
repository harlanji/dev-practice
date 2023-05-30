# Wagtail CMS Integrations

A large unorganized sample of working Wagtail CMS code testing various points.

Doesn't actually run, may be able to drop into stock CRX 2.1/Wagtail 4.2 site and figure it out.

## Dev Practice

* Populate content for a Wagtail/CodeRed Extensions site
* Implement an audit log of all model changes (django-auditlog)
* Migrate DB and environment to another machine
* Make environment run on Windows (not included here, noted for my own record)
* External read-only content DB from another application (Hogumathi Tweet Cache)
* Creating a Django snippet to get a list of Tweets, understand Snippets
* Creating a StreamField Block to get a list of Tweets, understand custom Blocks
* Create a chooser to search and select individual Tweets via Generic Chooser, first class integration smoke test
* Create a RoutablePageMixin (RPM) to experiment with models and rendering
* Fix issue with RPM where get_preview_context was not used
