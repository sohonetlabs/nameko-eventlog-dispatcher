from datetime import datetime, timezone

from nameko_eventlog_dispatcher.eventlog_dispatcher import _get_utcnow


def test__get_utcnow():
    result = _get_utcnow()

    assert isinstance(result, datetime)
    assert result.tzinfo == timezone.utc
