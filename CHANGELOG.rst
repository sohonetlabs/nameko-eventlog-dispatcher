Release Notes
=============

Here you can see the full list of changes between
nameko-eventlog-dispatcher versions, where semantic versioning is used:
*major.minor.patch*.

Backwards-compatible changes increment the minor version number only.

Version 0.3.0
-------------

* Updated to support Nameko 2.11 (this breaks compatibilty with older Nameko
  versions)
* Drop support for Python 3.3
* Support Python 3.5, 3.6 and 3.7

Version 0.2.0
-------------

Released 2017-06-23

* Use service name as source service, instead of ``all``, when dispatching Nameko events automatically.
* Add the ability to override the default Nameko ``event_type`` (used for the event logs) in the service config.
* Add ``MANIFEST.in``
* Add a ``metadata`` argument to the ``dispatch`` function to provide extra event metadata.

Version 0.1.0
-------------

Released 2017-06-19

* First release of the library.
* Add ability to manually dispatch event logs.
* Add ability to dispatch event logs when entrypoints are fired.
