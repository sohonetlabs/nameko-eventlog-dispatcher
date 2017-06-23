from datetime import datetime, timezone
from unittest.mock import call, Mock, patch

import pytest
from nameko.events import event_handler
from nameko.rpc import rpc
from nameko.testing.services import (
    dummy,
    entrypoint_hook,
    EntrypointWaiterTimeout,
    entrypoint_waiter,
)
from nameko.web.handlers import http

from nameko_eventlog_dispatcher import EventLogDispatcher


@pytest.fixture
def utcnow_mock():
    with patch(
        'nameko_eventlog_dispatcher.eventlog_dispatcher._get_utcnow'
    ) as m:
        m.return_value = datetime(
            2017, 5, 8, 15, 22, 43, 446796, tzinfo=timezone.utc
        )
        yield m


class TestService:

    name = "test_service"

    eventlog_dispatcher = EventLogDispatcher()

    @rpc
    def rpc_entrypoint(self):
        pass

    @http('GET', '/test')
    def http_entrypoint(self, request):
        pass

    @dummy
    def dummy_entrypoint(self):
        pass

    @dummy
    def log_event_method(self, event_data=None, metadata=None):
        if event_data:
            if metadata:
                self.eventlog_dispatcher(
                    'my_event_type', event_data, metadata
                )
            else:
                self.eventlog_dispatcher('my_event_type', event_data)
        else:
            if metadata:
                self.eventlog_dispatcher('my_event_type', metadata=metadata)
            else:
                self.eventlog_dispatcher('my_event_type')

    @event_handler('test_service', 'log_event')
    def log_event_handler(self, body):
        return body

    @event_handler('test_service', 'custom_event_type')
    def custom_event_type_handler(self, body):
        return body


class TestDispatchEventsAutomatically:

    def test_rpc_call_when_set_to_auto_capture(
        self, container_factory, config, utcnow_mock
    ):
        config['EVENTLOG_DISPATCHER'] = {'auto_capture': True}
        container = container_factory(TestService, config)
        container.start()

        with entrypoint_waiter(
            container, 'log_event_handler', timeout=1
        ) as result:
            with entrypoint_hook(
                container, 'rpc_entrypoint'
            ) as rpc_entrypoint:
                rpc_entrypoint()

        expected_body = result.get()
        call_id = expected_body.pop('call_id')
        call_stack = expected_body.pop('call_stack')

        assert call_id.startswith('test_service.rpc_entrypoint.')
        assert len(call_stack) == 1
        assert call_stack[0].startswith('test_service.rpc_entrypoint.')
        assert expected_body == {
            'data': {},
            'entrypoint_name': 'rpc_entrypoint',
            'entrypoint_protocol': 'Rpc',
            'service_name': 'test_service',
            'timestamp': '2017-05-08T15:22:43+00:00',
            'event_type': 'entrypoint_fired',
        }

    def test_http_call_when_set_to_auto_capture(
        self, container_factory, config, utcnow_mock, web_session
    ):
        config['EVENTLOG_DISPATCHER'] = {'auto_capture': True}
        container = container_factory(TestService, config)
        container.start()

        with entrypoint_waiter(
            container, 'log_event_handler', timeout=1
        ) as result:
            web_session.get('/test')

        expected_body = result.get()
        call_id = expected_body.pop('call_id')
        call_stack = expected_body.pop('call_stack')

        assert call_id.startswith('test_service.http_entrypoint.')
        assert len(call_stack) == 1
        assert call_stack[0].startswith('test_service.http_entrypoint.')
        assert expected_body == {
            'data': {},
            'entrypoint_name': 'http_entrypoint',
            'entrypoint_protocol': 'HttpRequestHandler',
            'service_name': 'test_service',
            'timestamp': '2017-05-08T15:22:43+00:00',
            'event_type': 'entrypoint_fired',
        }


class TestDoNotDispatchEventsAutomatically:

    def test_rpc_call_when_set_to_auto_capture_and_method_excluded(
        self, container_factory, config, utcnow_mock
    ):
        config['EVENTLOG_DISPATCHER'] = {
            'auto_capture': True,
            'entrypoints_to_exclude': ['test_1', 'rpc_entrypoint', 'test_2'],
        }
        container = container_factory(TestService, config)
        container.start()

        with pytest.raises(EntrypointWaiterTimeout):
            with entrypoint_waiter(container, 'log_event_handler', timeout=1):
                with entrypoint_hook(
                    container, 'rpc_entrypoint'
                ) as rpc_entrypoint:
                    rpc_entrypoint()

    def test_rpc_call_when_not_set_to_auto_capture(
        self, container_factory, config
    ):
        container = container_factory(TestService, config)
        container.start()

        with pytest.raises(EntrypointWaiterTimeout):
            with entrypoint_waiter(container, 'log_event_handler', timeout=1):
                with entrypoint_hook(
                    container, 'rpc_entrypoint'
                ) as rpc_entrypoint:
                    rpc_entrypoint()

    def test_http_call_when_not_set_to_auto_capture(
        self, container_factory, config, web_session
    ):
        container = container_factory(TestService, config)
        container.start()

        with pytest.raises(EntrypointWaiterTimeout):
            with entrypoint_waiter(container, 'log_event_handler', timeout=1):
                web_session.get('/test')

    @pytest.mark.parametrize('auto_capture', [True, False])
    def test_dummy_call(
        self, container_factory, config, utcnow_mock, auto_capture
    ):
        config['EVENTLOG_DISPATCHER'] = {'auto_capture': auto_capture}
        container = container_factory(TestService, config)
        container.start()

        with pytest.raises(EntrypointWaiterTimeout):
            with entrypoint_waiter(container, 'log_event_handler', timeout=1):
                with entrypoint_hook(
                    container, 'dummy_entrypoint'
                ) as dummy_entrypoint:
                    dummy_entrypoint()


class TestUnexpectedErrors:

    @pytest.fixture
    def event_dispatcher_mock(self):
        with patch(
            'nameko_eventlog_dispatcher.eventlog_dispatcher.event_dispatcher'
        ) as m:
            yield m

    @pytest.fixture
    def log_mock(self):
        with patch('nameko_eventlog_dispatcher.eventlog_dispatcher.log') as m:
            yield m

    def test_worker_setup_raises(
        self, container_factory, config, utcnow_mock, event_dispatcher_mock,
        log_mock
    ):
        config['EVENTLOG_DISPATCHER'] = {'auto_capture': True}
        container = container_factory(TestService, config)
        container.start()

        exception = Exception('BOOOM!!')
        # `get_dependency` makes the first call
        event_dispatcher_mock.side_effect = [Mock(), exception]

        with pytest.raises(EntrypointWaiterTimeout):
            with entrypoint_waiter(container, 'log_event_handler', timeout=1):
                with entrypoint_hook(
                    container, 'rpc_entrypoint'
                ) as rpc_entrypoint:
                    rpc_entrypoint()

        assert log_mock.error.call_args_list == [call(exception)]


class TestDispatchEventsMaually:

    @pytest.mark.parametrize(
        'auto_capture, event_data, expected_data',
        [
            (True, None, {}),
            (True, {'a': 1}, {'a': 1}),
            (False, None, {}),
            (False, {'a': 1}, {'a': 1}),
        ]
    )
    def test_dispatch_event(
        self, container_factory, config, utcnow_mock, auto_capture, event_data,
        expected_data
    ):
        config['EVENTLOG_DISPATCHER'] = {'auto_capture': auto_capture}
        container = container_factory(TestService, config)
        container.start()

        with entrypoint_waiter(
            container, 'log_event_handler', timeout=1
        ) as result:
            with entrypoint_hook(container, 'log_event_method') as log_event:
                log_event(event_data)

        expected_body = result.get()
        call_id = expected_body.pop('call_id')
        call_stack = expected_body.pop('call_stack')

        assert call_id.startswith('test_service.log_event_method.')
        assert len(call_stack) == 1
        assert call_stack[0].startswith('test_service.log_event_method.')
        assert expected_body == {
            'data': expected_data,
            'entrypoint_name': 'log_event_method',
            'entrypoint_protocol': 'Entrypoint',
            'service_name': 'test_service',
            'timestamp': '2017-05-08T15:22:43+00:00',
            'event_type': 'my_event_type',
        }

    def test_dispatch_event_with_custom_generic_event_type(
        self, container_factory, config, utcnow_mock
    ):
        config['EVENTLOG_DISPATCHER'] = {'event_type': 'custom_event_type'}
        container = container_factory(TestService, config)
        container.start()

        with entrypoint_waiter(
            container, 'custom_event_type_handler', timeout=1
        ) as result:
            with entrypoint_hook(container, 'log_event_method') as log_event:
                log_event({'a': 1})

        expected_body = result.get()
        call_id = expected_body.pop('call_id')
        call_stack = expected_body.pop('call_stack')

        assert call_id.startswith('test_service.log_event_method.')
        assert len(call_stack) == 1
        assert call_stack[0].startswith('test_service.log_event_method.')
        assert expected_body == {
            'data': {'a': 1},
            'entrypoint_name': 'log_event_method',
            'entrypoint_protocol': 'Entrypoint',
            'service_name': 'test_service',
            'timestamp': '2017-05-08T15:22:43+00:00',
            'event_type': 'my_event_type',
        }

    def test_dispatch_event_with_additional_metadata(
        self, container_factory, config, utcnow_mock
    ):
        container = container_factory(TestService, config)
        container.start()

        with entrypoint_waiter(
            container, 'log_event_handler', timeout=1
        ) as result:
            with entrypoint_hook(container, 'log_event_method') as log_event:
                log_event({'a': 1}, {'b': 2})

        expected_body = result.get()
        call_id = expected_body.pop('call_id')
        call_stack = expected_body.pop('call_stack')

        assert call_id.startswith('test_service.log_event_method.')
        assert len(call_stack) == 1
        assert call_stack[0].startswith('test_service.log_event_method.')
        assert expected_body == {
            'data': {'a': 1},
            'b': 2,
            'entrypoint_name': 'log_event_method',
            'entrypoint_protocol': 'Entrypoint',
            'service_name': 'test_service',
            'timestamp': '2017-05-08T15:22:43+00:00',
            'event_type': 'my_event_type',
        }
