Release Notes
=============

Here you can see the full list of changes between
nameko-eventlog-dispatcher versions, where semantic versioning is used:
*major.minor.patch*.

Backwards-compatible changes increment the minor version number only.

Version 0.2.0
-------------

Released 2017-06-*

* Use service name as source service, instead of "all", when dispatching Nameko events automatically.
* Rename EVENT_TYPE class attribute to GENERIC_EVENT_TYPE.
* Add the ability to provide both `generic` and `entrypoint_fired` `event_types` in the service config.

Version 0.1.0
-------------

Released 2017-06-19

* First release of the library.
* Add ability to manually dispatch event logs.
* Add ability to dispatch event logs when entrypoints are fired.
