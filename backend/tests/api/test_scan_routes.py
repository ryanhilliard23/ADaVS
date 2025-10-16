import pytest

def test_list_scans_calls_service(client, monkeypatch):
    from app.services import scan_services

    def fake_list_scans(db):
        return [{"id": 7, "status": "completed", "targets": "127.0.0.1"}]

    monkeypatch.setattr(scan_services, "list_scans", fake_list_scans)

    r = client.get("/api/scans/")
    assert r.status_code == 200
    assert r.json() == [{"id": 7, "status": "completed", "targets": "127.0.0.1"}]

def test_scan_detail_found(client, monkeypatch):
    from app.services import scan_services
    monkeypatch.setattr(scan_services, "scan_detail", lambda db, sid: {"id": sid, "status": "running"})

    r = client.get("/api/scans/42")
    assert r.status_code == 200
    assert r.json() == {"id": 42, "status": "running"}

def test_scan_detail_404(client, monkeypatch):
    from app.services import scan_services
    monkeypatch.setattr(scan_services, "scan_detail", lambda db, sid: None)

    r = client.get("/api/scans/9999")
    assert r.status_code == 404
    assert r.json()["detail"] == "Scan not found"

def test_start_scan_posts_targets_and_uses_service(client, monkeypatch):
    from app.services import scan_services
    seen = {}

    def fake_start_scan(db, targets: str):
        seen["targets"] = targets
        return {"id": 101, "status": "pending", "targets": targets}

    monkeypatch.setattr(scan_services, "start_scan", fake_start_scan)

    r = client.post("/api/scans/", json={"targets": "10.0.0.0/24"})
    assert r.status_code == 200
    assert r.json()["id"] == 101
    assert seen["targets"] == "10.0.0.0/24"
