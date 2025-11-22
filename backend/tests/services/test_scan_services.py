import types
from app.models.scan import Scan
from app.services import scan_services
from app.models.user import User
import pytest


def test_list_scans_and_detail(db_session):
    s1 = Scan(status="running", targets="127.0.0.1")
    s2 = Scan(status="completed", targets="8.8.8.8")
    db_session.add_all([s1, s2])
    db_session.commit()

    lst = scan_services.list_scans(db_session, user_id=1)
    assert len(lst) == 2

    d = scan_services.scan_detail(db_session, s2.id, user_id=1)
    assert d["id"] == s2.id
    assert d["status"] == "completed"


def test_start_scan_success_creates_assets_and_services(db_session, monkeypatch):
    class FakeResp:
        status_code = 200

        def json(self):
            return {"xml": "<nmap xml>...</nmap>"}

    monkeypatch.setattr(
        scan_services, "requests", types.SimpleNamespace(post=lambda *a, **k: FakeResp())
    )

    def fake_parse(xml):
        return [
            {
                "ip_address": "10.0.0.5",
                "hostname": "api",
                "os": "ubuntu",
                "services": [
                    {"port": 80, "protocol": "tcp", "service_name": "http", "banner": "nginx"},
                    {"port": 53, "protocol": "udp", "service_name": "dns", "banner": "bind"},
                ],
            }
        ]

    monkeypatch.setattr(scan_services, "parse_nmap_xml", fake_parse)
    monkeypatch.setattr(scan_services, "validate_parsed_data", lambda hosts: True)

    monkeypatch.setenv("VPS_SCANNER_URL", "http://fake-scanner")
    monkeypatch.setenv("SCANNER_TOKEN", "secret")

    out = scan_services.start_scan(db_session, "10.0.0.0/24", user_id=1)
    assert out["status"] == "completed"
    assert out["hosts_discovered"] == 1
    assert out["assets_created"] == 1
    assert out["services_created"] == 2

    detail = scan_services.scan_detail(db_session, out["scan_id"], user_id=1)
    assert len(detail["assets"]) == 1
    assert detail["assets"][0]["ip_address"] == "10.0.0.5"


def test_start_scan_failure_non_200(db_session, monkeypatch):
    class FakeResp:
        status_code = 500
        text = "boom"

        def json(self):
            return {}

    monkeypatch.setattr(
        scan_services, "requests", types.SimpleNamespace(post=lambda *a, **k: FakeResp())
    )
    monkeypatch.setattr(scan_services, "parse_nmap_xml", lambda xml: [])
    monkeypatch.setattr(scan_services, "validate_parsed_data", lambda hosts: False)

    out = scan_services.start_scan(db_session, "badtarget", user_id=1)
    assert out["status"] == "failed"
    assert "error" in out


def test_start_scan_failure_bad_parse(db_session, monkeypatch):
    class OkResp:
        status_code = 200

        def json(self):
            return {"xml": "<xml/>"}

    monkeypatch.setattr(
        scan_services, "requests", types.SimpleNamespace(post=lambda *a, **k: OkResp())
    )
    monkeypatch.setattr(scan_services, "parse_nmap_xml", lambda xml: [])
    monkeypatch.setattr(scan_services, "validate_parsed_data", lambda hosts: False)

    out = scan_services.start_scan(db_session, "10.0.0.0/24", user_id=1)
    assert out["status"] == "failed"

def test_start_scan_failure_no_xml(db_session, monkeypatch):
    class OkNoXMLResp:
        status_code = 200
        def json(self):
            return {} 
    monkeypatch.setattr(
        scan_services, "requests", type("req", (), {"post": lambda *a, **k: OkNoXMLResp()})
    )
    out = scan_services.start_scan(db_session, "no-xml", user_id=1)
    assert out["status"] == "failed"
    assert "No XML" in out["error"]


def test_start_scan_handles_nuclei_exception(db_session, monkeypatch):
    class FakeResp:
        status_code = 200
        def json(self):
            # valid minimal XML structure
            return {"xml": "<nmaprun><host><status state='up'/><address addr='1.2.3.4' addrtype='ipv4'/><ports><port portid='80' protocol='tcp'><state state='open'/><service name='http'/></port></ports></host></nmaprun>"}
    monkeypatch.setattr(
        scan_services, "requests", type("req", (), {"post": lambda *a, **k: FakeResp()})
    )
    monkeypatch.setattr(scan_services, "parse_nmap_xml", lambda xml: [{
        "ip_address": "1.2.3.4",
        "hostname": None,
        "os": None,
        "services": [{"port": 80, "protocol": "tcp", "service_name": "http", "banner": None}],
    }])
    monkeypatch.setattr(scan_services, "validate_parsed_data", lambda h: True)
    monkeypatch.setattr(scan_services, "run_nuclei_scan", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("nuclei fail")))
    monkeypatch.setenv("VPS_SCANNER_URL", "http://fake")
    monkeypatch.setenv("SCANNER_TOKEN", "tok")

    result = scan_services.start_scan(db_session, "1.2.3.4", user_id=5)
    # even with nuclei failure, status should still complete
    assert result["status"] == "completed"
    assert "hosts_discovered" in result
    assert result["assets_created"] >= 1

def test_start_public_scan_success(db_session, monkeypatch):
    from app.services import scan_services
    
    # Mock the recon service to return fake OSINT data
    def fake_discover(domain):
        return [
            {
                "ip_address": "1.1.1.1",
                "hostname": "one.one.one.one",
                "os": "Linux",
                "services": [
                    {"port": 443, "protocol": "tcp", "service_name": "https", "banner": "cloudflare"}
                ]
            }
        ]

    monkeypatch.setattr(scan_services, "discover_domain_assets", fake_discover)

    # Execute public scan
    result = scan_services.start_scan(
        db_session, 
        targets="example.com", 
        user_id=1, 
        scan_type="public"
    )

    assert result["status"] == "completed"
    assert result["hosts_discovered"] == 1
    
    # Verify it actually hit the DB
    detail = scan_services.scan_detail(db_session, result["scan_id"], user_id=1)
    assert detail["assets"][0]["ip_address"] == "1.1.1.1"
