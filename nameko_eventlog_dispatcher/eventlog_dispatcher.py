import logging
from copy import deepcopy
from datetime import datetime, timezone

from kombu.common import maybe_declare
from nameko.amqp import get_connection, verify_amqp_uri
from nameko.events import EventDispatcher
from nameko.rpc import Rpc
from nameko.standalone.events import event_dispatcher, get_event_exchange
from nameko.web.handlers import HttpRequestHandler


log = logging.getLogger(__name__)


class EventLogDispatcher(EventDispatcher):

    """Dispatcher of event logs.

    When the auto capture feature is enabled, it dispatches an event
    each time an entrypoint is fired.

    Also provides the ability to manually dispatch event logs,
    optionally providing related event data.

    On both cases, relevant worker context information is added to the
    event data.
    """

    ENTRYPOINT_FIRED = 'entrypoint_fired'
    """Event type used by events triggered when entrypoints are fired."""

    EVENT_TYPE = 'log_event'
    """Event type used by log events dispatched from the entrypoints."""

    SOURCE_SERVICE = 'all'
    """Source service name used when auto capturing events."""

    ENTRYPOINT_TYPES_TO_LOG = (Rpc, HttpRequestHandler)
    """Sequence of entrypoint types to auto capture event logs from."""

    def setup(self):
        super().setup()

        config = self.container.config.get('EVENTLOG_DISPATCHER', {})
        self.auto_capture = config.get('auto_capture') or False
        self.entrypoints_to_exclude = config.get(
            'entrypoints_to_exclude'
        ) or []

        if self.auto_capture and self.SOURCE_SERVICE is not None:
            self._declare_additional_exchange()

    def worker_setup(self, worker_ctx):
        super().worker_setup(worker_ctx)

        if not self._should_dispatch(worker_ctx.entrypoint):
            return

        try:
            self._get_dispatch(
                worker_ctx, source_service=self.SOURCE_SERVICE
            )(event_type=self.ENTRYPOINT_FIRED)
        except Exception as exc:
            log.error(exc)

    def get_dependency(self, worker_ctx):
        return self._get_dispatch(worker_ctx)

    def _get_dispatch(self, worker_ctx, source_service=None):
        headers = self.get_message_headers(worker_ctx)
        kwargs = self.kwargs
        dispatcher = event_dispatcher(self.config, headers=headers, **kwargs)

        if source_service is None:
            source_service = self.service_name

        body = self._get_base_call_info(worker_ctx)

        def dispatch(event_type, event_data=None):
            body['timestamp'] = _get_formatted_utcnow()
            body['event_type'] = event_type
            body['data'] = event_data or {}

            if event_type == self.ENTRYPOINT_FIRED:
                disp_event_type = self.ENTRYPOINT_FIRED
            else:
                disp_event_type = self.EVENT_TYPE

            dispatcher(source_service, disp_event_type, body)

        return dispatch

    def _get_base_call_info(self, worker_ctx):
        entrypoint = worker_ctx.entrypoint
        return {
            'service_name': worker_ctx.service_name,
            'entrypoint_protocol': type(entrypoint).__name__,
            'entrypoint_name': entrypoint.method_name,
            'call_id': worker_ctx.call_id,
            'call_stack': deepcopy(worker_ctx.call_id_stack),
        }

    def _declare_additional_exchange(self):
        common_exchange = get_event_exchange(self.SOURCE_SERVICE)
        if common_exchange is not None:
            verify_amqp_uri(self.amqp_uri)
            with get_connection(self.amqp_uri) as conn:
                maybe_declare(common_exchange, conn)

    def _should_dispatch(self, entrypoint):
        return (
            self.auto_capture and
            isinstance(entrypoint, self.ENTRYPOINT_TYPES_TO_LOG) and
            entrypoint.method_name not in self.entrypoints_to_exclude
        )


def _get_formatted_utcnow():
    return _get_utcnow().replace(microsecond=0).isoformat()


def _get_utcnow():
    return datetime.now(tz=timezone.utc)
