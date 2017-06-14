from unittest.mock import call, patch

import pytest
from kombu import Exchange

from nameko_eventlog_dispatcher import EventLogDispatcher
from nameko_eventlog_dispatcher.eventlog_dispatcher import EventDispatcher


class TestEventLogDispatcherSetup:

    @pytest.fixture
    def super_setup_mock(self):
        with patch.object(EventDispatcher, 'setup') as m:
            yield m

    @pytest.fixture
    def maybe_declare_mock(self):
        with patch(
            'nameko_eventlog_dispatcher.eventlog_dispatcher.maybe_declare'
        ) as m:
            yield m

    def test_setup_with_default_params(self, mock_container, super_setup_mock):
        dependency_provider = EventLogDispatcher().bind(
            mock_container, 'eventlog_dispatcher'
        )

        dependency_provider.setup()

        assert super_setup_mock.call_args_list == [call()]
        assert dependency_provider.auto_capture is False
        assert dependency_provider.entrypoints_to_exclude == []

    def test_setup_with_empty_params(self, mock_container, super_setup_mock):
        mock_container.config['EVENTLOG_DISPATCHER'] = {
            'auto_capture': None,
            'entrypoints_to_exclude': None,
        }
        dependency_provider = EventLogDispatcher().bind(
            mock_container, 'eventlog_dispatcher'
        )

        dependency_provider.setup()

        assert super_setup_mock.call_args_list == [call()]
        assert dependency_provider.auto_capture is False
        assert dependency_provider.entrypoints_to_exclude == []

    def test_setup_with_provided_params(
        self, mock_container, super_setup_mock, config
    ):
        config['EVENTLOG_DISPATCHER'] = {
            'auto_capture': True,
            'entrypoints_to_exclude': ['test_1', 'test_2'],
        }
        mock_container.config = config
        dependency_provider = EventLogDispatcher().bind(
            mock_container, 'eventlog_dispatcher'
        )

        dependency_provider.setup()

        assert super_setup_mock.call_args_list == [call()]
        assert dependency_provider.auto_capture is True
        assert dependency_provider.entrypoints_to_exclude == [
            'test_1', 'test_2'
        ]

    def test_setup_declares_exchange_when_set_to_auto_capture(
        self, mock_container, super_setup_mock, config, maybe_declare_mock
    ):
        config['EVENTLOG_DISPATCHER'] = {
            'auto_capture': True,
            'entrypoints_to_exclude': ['test_1', 'test_2'],
        }
        mock_container.config = config
        dependency_provider = EventLogDispatcher().bind(
            mock_container, 'eventlog_dispatcher'
        )

        dependency_provider.setup()

        exchange = maybe_declare_mock.call_args_list[0][0][0]
        assert maybe_declare_mock.call_count == 1
        assert isinstance(exchange, Exchange)
        assert exchange.name == 'all.events'
