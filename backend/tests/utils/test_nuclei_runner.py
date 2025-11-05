import pytest
from unittest.mock import Mock, patch
from app.utils import nuclei_runner


@pytest.fixture
def mock_db():
    """Simple fake DB with query, filter, etc."""
    mock = Mock()
    mock.query.return_value.filter.return_value.scalar.return_value = 1
    return mock


def test_no_services(monkeypatch, mock_db, capsys):
    """Case: when no services are found."""
    # return empty list for .all()
    mock_db.query.return_value.join.return_value.join.return_value.filter.return_value.order_by.return_value.all.return_value = []

    result = nuclei_runner.run_nuclei_scan(mock_db, 99, ["1.1.1.1"])
    assert result["status"] == "no_targets"
    assert result["services_count"] == 0
    assert "No services found" in capsys.readouterr().out


def test_request_fails(monkeypatch, mock_db):
    """Case: when requests.post throws."""
    mock_svc = Mock()
    mock_svc.asset.ip_address = "1.2.3.4"
    mock_svc.port = 80
    mock_svc.service_name = "http"

    mock_db.query.return_value.join.return_value.join.return_value.filter.return_value.order_by.return_value.all.return_value = [mock_svc]
    mock_db.query.return_value.filter.return_value.scalar.return_value = 1

    monkeypatch.setattr(nuclei_runner, "requests", Mock())
    nuclei_runner.requests.post.side_effect = Exception("boom")

    result = nuclei_runner.run_nuclei_scan(mock_db, 1, ["1.2.3.4"])
    assert result["status"] == "failed"
    assert "boom" in result["error"]


def test_runner_returns_non_list(monkeypatch, mock_db, capsys):
    """Case: runner returns non-list JSON."""
    mock_svc = Mock()
    mock_svc.asset.ip_address = "1.2.3.4"
    mock_svc.port = 443
    mock_svc.service_name = "https"
    mock_svc.id = 1

    mock_db.query.return_value.join.return_value.join.return_value.filter.return_value.order_by.return_value.all.return_value = [mock_svc]
    mock_db.query.return_value.filter.return_value.scalar.return_value = 1

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"bad": "data"}
    mock_response.raise_for_status.return_value = None

    with patch("app.utils.nuclei_runner.requests.post", return_value=mock_response):
        with patch("app.utils.nuclei_runner.wake_db_up"):
            res = nuclei_runner.run_nuclei_scan(mock_db, 5, ["1.2.3.4"])

    out = capsys.readouterr().out
    assert "Unexpected JSON" in out
    assert res["status"] == "ok"



def test_runner_skips_existing_vuln(monkeypatch, mock_db):
    """Case: nuclei result already exists, should skip insert."""
    mock_svc = Mock()
    mock_svc.asset.ip_address = "1.2.3.4"
    mock_svc.port = 8080
    mock_svc.service_name = "api"
    mock_svc.id = 99

    mock_db.query.return_value.join.return_value.join.return_value.filter.return_value.order_by.return_value.all.return_value = [mock_svc]
    mock_db.query.return_value.filter.return_value.scalar.return_value = 1
    mock_db.query.return_value.filter.return_value.first.return_value = Mock()  # existing vuln

    nuclei_results = [{
        "template-id": "T-001",
        "info": {"severity": "low", "name": "already-there"},
        "matched-at": "http://1.2.3.4:8080"
    }]

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = nuclei_results
    mock_response.raise_for_status.return_value = None

    with patch("app.utils.nuclei_runner.requests.post", return_value=mock_response):
        with patch("app.utils.nuclei_runner.wake_db_up"):
            result = nuclei_runner.run_nuclei_scan(mock_db, 5, ["1.2.3.4"])

    assert result["status"] == "ok"
    assert result["inserted"] == 0
