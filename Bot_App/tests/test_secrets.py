from datetime import datetime
from Bot_App.config import secrets


def test_check_time_of_day_true(monkeypatch):
    """Check function returns True when hour and minute match."""

    class DummyDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime(2024, 1, 1, 10, 15)

    monkeypatch.setattr(secrets, "datetime", DummyDatetime)
    assert secrets.check_time_of_day(10, 15)


def test_check_time_of_day_false(monkeypatch):
    """Check function returns False when hour/minute don't match."""

    class DummyDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime(2024, 1, 1, 10, 15)

    monkeypatch.setattr(secrets, "datetime", DummyDatetime)
    assert not secrets.check_time_of_day(9, 30)
