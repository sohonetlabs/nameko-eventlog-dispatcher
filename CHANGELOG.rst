Version History
===============

Here you can see the full list of changes between
nameko-eventlog-dispatcher versions, where semantic versioning is used:
*major.minor.patch*.

Backwards-compatible changes increment the minor version number only.


0.4.1
-----

Released 2019-03-21

* Add Nameko ``2.12`` support (#16)
* Ensure that Tox can be run cleanly locally (#15)


0.4.0
-----

Released 2019-03-15

* Add support for Python 3.7 (#12)
* Add support for older Nameko versions: ``2.6``, ``2.7``, ``2.8``,
  ``2.9``, ``2.10``, ``2.11`` (#13, #14)


0.3.0
-----

Released 2019-01-28

* Updated to support Nameko 2.11 (**this breaks compatibilty with
  older Nameko versions**) (#8)
* Drop support for Python 3.3 (#8)
* Support Python 3.5 and 3.6 (#8)


0.2.0
-----

Released 2017-06-23

* Use service name as source service, instead of ``all``, when
  dispatching Nameko events automatically.
* Add the ability to override the default Nameko ``event_type`` (used
  for the event logs) in the service config.
* Add ``MANIFEST.in``
* Add a ``metadata`` argument to the ``dispatch`` function to provide
  extra event metadata.

0.1.0
-----

Released 2017-06-19

* First release of the library.
* Add ability to manually dispatch event logs.
* Add ability to dispatch event logs when entrypoints are fired.
