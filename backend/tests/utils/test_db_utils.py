import pytest
from unittest.mock import Mock
from sqlalchemy.exc import OperationalError

from app.utils.db_utils import wake_db_up

def test_wake_db_up_success(monkeypatch, capsys):
    mock_db = Mock()
    wake_db_up(mock_db)
    mock_db.execute.assert_called_once()
    mock_db.commit.assert_called_once()
    out = capsys.readouterr().out
    assert "DB connection verified and awake" in out


def test_wake_db_up_reconnect_success(monkeypatch, capsys):
    mock_db = Mock()

    # fail first call, succeed on retry
    calls = {"count": 0}

    def execute_side_effect(_):
        if calls["count"] == 0:
            calls["count"] += 1
            raise Exception("initial failure")
        return True

    mock_db.execute.side_effect = execute_side_effect
    wake_db_up(mock_db)

    # After the failure, it should retry
    assert mock_db.execute.call_count == 2
    out = capsys.readouterr().out
    assert "DB likely suspended" in out
    assert "Reconnected successfully" in out


def test_wake_db_up_reconnect_failure(monkeypatch, capsys):
    mock_db = Mock()

    mock_db.execute.side_effect = Exception("db down")

    with pytest.raises(Exception):
        wake_db_up(mock_db)

    out = capsys.readouterr().out
    assert "Failed to reconnect" in out
