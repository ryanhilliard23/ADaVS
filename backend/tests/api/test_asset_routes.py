import pytest

def test_list_assets_calls_service_and_returns_json(client, monkeypatch):
    # arrange
    called = {}
    def fake_list_assets(db):
        called["hit"] = True
        return [{"id": 1, "ip_address": "10.0.0.5"}]

    from app.services import asset_services
    monkeypatch.setattr(asset_services, "list_assets", fake_list_assets)

    # act
    r = client.get("/api/assets/")

    # assert
    assert r.status_code == 200
    assert called.get("hit") is True
    assert r.json() == [{"id": 1, "ip_address": "10.0.0.5"}]

def test_asset_detail_returns_stub_message(client):
    r = client.get("/api/assets/123")
    assert r.status_code == 200
    assert r.json() == {"message": "Asset 123 endpoint hit successfully!"}
