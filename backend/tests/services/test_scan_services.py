# backend/tests/services/test_scan_services.py
import types
from app.models.scan import Scan
from app.services import scan_services

def test_list_scans_and_detail(db_session):
    s1 = Scan(status="running", targets="127.0.0.1")
    s2 = Scan(status="completed", targets="8.8.8.8")
    db_session.add_all([s1, s2]); db_session.commit()

    lst = scan_services.list_scans(db_session)
    assert len(lst) == 2
    d = scan_services.scan_detail(db_session, s2.id)
    assert d["id"] == s2.id
    assert d["status"] == "completed"

def test_start_scan_success_creates_assets_and_services(db_session, monkeypatch):
    # stub HTTP call to VPS
    class FakeResp:
        status_code = 200
        def json(self):
            return {"xml": "<nmap xml>...</nmap>"}
    monkeypatch.setattr(scan_services, "requests", types.SimpleNamespace(post=lambda *a, **k: FakeResp()))

    # stub parser + validator to return deterministic hosts
    def fake_parse(xml):
        return [{
            "ip_address": "10.0.0.5",
            "hostname": "api",
            "os": "ubuntu",
            "services": [
                {"port": 80, "protocol": "tcp", "service_name": "http", "banner": "nginx"},
                {"port": 53, "protocol": "udp", "service_name": "dns", "banner": "bind"},
            ],
        }]
    monkeypatch.setattr(scan_services, "parse_nmap_xml", fake_parse)
    monkeypatch.setattr(scan_services, "validate_parsed_data", lambda hosts: True)

    # env vars not strictly needed since we stubbed requests, but keep them sane
    monkeypatch.setenv("VPS_SCANNER_URL", "http://fake-scanner")
    monkeypatch.setenv("SCANNER_TOKEN", "secret")

    out = scan_services.start_scan(db_session, "10.0.0.0/24")
    assert out["status"] == "completed"
    assert out["hosts_discovered"] == 1
    assert out["assets_created"] == 1
    assert out["services_created"] == 2

    # the DB should reflect the created objects
    detail = scan_services.scan_detail(db_session, out["scan_id"])
    assert len(detail["assets"]) == 1
    assert detail["assets"][0]["ip_address"] == "10.0.0.5"

def test_start_scan_failure_non_200(db_session, monkeypatch):
    class FakeResp:
        status_code = 500
        text = "boom"
        def json(self): return {}
    monkeypatch.setattr(scan_services, "requests", types.SimpleNamespace(post=lambda *a, **k: FakeResp()))
    monkeypatch.setattr(scan_services, "parse_nmap_xml", lambda xml: [])
    monkeypatch.setattr(scan_services, "validate_parsed_data", lambda hosts: False)

    out = scan_services.start_scan(db_session, "badtarget")
    assert out["status"] == "failed"
    assert "error" in out

def test_start_scan_failure_bad_parse(db_session, monkeypatch):
    class OkResp:
        status_code = 200
        def json(self): return {"xml": "<xml/>"}
    monkeypatch.setattr(scan_services, "requests", types.SimpleNamespace(post=lambda *a, **k: OkResp()))
    monkeypatch.setattr(scan_services, "parse_nmap_xml", lambda xml: [])
    monkeypatch.setattr(scan_services, "validate_parsed_data", lambda hosts: False)

    out = scan_services.start_scan(db_session, "10.0.0.0/24")
    assert out["status"] == "failed"
