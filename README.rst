Nameko eventlog dispatcher
==========================

.. pull-quote::

    `Nameko <http://nameko.readthedocs.org>`_ dependency provider that
    dispatches log data using ``Events`` (Pub-Sub).


.. image:: https://travis-ci.org/sohonetlabs/nameko-eventlog-dispatcher.svg?branch=master


Usage
-----

Dispatching event log data
``````````````````````````

Include the ``EventLogDispatcher`` dependency in your service class:

.. code-block:: python

    from nameko.rpc import rpc
    from nameko_eventlog_dispatcher import EventLogDispatcher


    class FooService:

        name = 'foo'

        eventlog_dispatcher = EventLogDispatcher()

        @rpc
        def foo_method(self):
            self.eventlog_dispatcher('foo_event_type', {'value': 1})

``event_type`` and  some ``event_data`` (optional) will be provided as
arguments. ``event_data`` must contain JSON serializable data.

Calling ``foo_method`` will dispatch an event from the ``foo`` service
with ``log_event`` as the event type.

Then, any nameko service will be able to handle this event.

.. code-block:: python

    from nameko.events import event_handler


    class BarService:

        name = 'bar'

        @event_handler('foo', 'log_event')
        def foo_log_event_handler(self, body):
            """`body` will contain the event log data."""


Capturing log data when entrypoints are fired
`````````````````````````````````````````````

Enable auto capture event logs in your nameko configuration file:

.. code-block:: yaml

    # config.yaml

    EVENTLOG_DISPATCHER:
      auto_capture: true
      entrypoints_to_exclude: []

With ``auto_capture`` set to ``true``, a nameko event will be dispatched
every time an entrypoint is fired:

- The source service for these events will be ``all``.
- The event type will be ``entrypoint_fired``.
- Only entrypoints listed in the ``ENTRYPOINT_TYPES_TO_LOG`` class
  attribute will be logged.
- ``entrypoints_to_exclude`` can be used to provide a list of entrypoint
  method names to exclude when firing events automatically.

Then, any nameko service will be able to handle this kind of events:

.. code-block:: python

    from nameko.events import event_handler


    class BazService:

        name = 'baz'

        @event_handler('all', 'entrypoint_fired')
        def all_entrypoint_fired_event_handler(self, body):
            """Body will contain the event log data."""


Format of the event log data
----------------------------

This is the format of the event log data:

.. code-block:: python

    {
      "entrypoint_name": "foo_method",
      "service_name": "foo",
      "timestamp": "2017-06-12T13:48:16+00:00",
      "event_type": "foo_event_type",
      "data": {},
      "call_stack": [
        "standalone_rpc_proxy.call.3f349ea4-ed3e-4a3b-93d0-a36fbf928ecb",
        "bla.bla_method.21d623b4-edc4-4232-9957-4fad72533b75",
        "foo.foo_method.d7e907ee-9425-48a6-84e6-89db19e3ce50"
      ],
      "entrypoint_protocol": "Rpc",
      "call_id": "foo.foo_method.d7e907ee-9425-48a6-84e6-89db19e3ce50"
    }

The ``data`` attribute will contain the event data that was provided as
an argument for the ``event_data`` parameter when dispatching the event.


Tests
-----

It is assumed that RabbitMQ is up and running on the default URL
``guest:guest@localhost`` and uses the default ports.

.. code-block:: bash

    $ make test
    $ make coverage

A different RabbitMQ URI can be provided overriding the following
environment variables: ``RABBIT_CTL_URI`` and ``AMQP_URI``.

Additional ``pytest`` parameters can be also provided using the ``ARGS``
variable.

.. code-block:: bash

    $ make test RABBIT_CTL_URI=http://guest:guest@dockermachine:15673 AMQP_URI=amqp://guest:guest@dockermachine:5673 ARGS='-x -vv --disable-pytest-warnings'
    $ make coverage RABBIT_CTL_URI=http://guest:guest@dockermachine:15673 AMQP_URI=amqp://guest:guest@dockermachine:5673 ARGS='-x -vv --disable-pytest-warnings'
