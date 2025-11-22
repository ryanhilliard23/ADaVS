# backend/tests/test_main.py
import importlib
import pytest
from starlette.testclient import TestClient
from fastapi.testclient import TestClient
from app.main import app as fastapi_app
from app.models.base import get_db


def _load_app(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite+pysqlite:///:memory:")
    import app.main as app_main
    importlib.reload(app_main)
    return app_main


def test_lifespan_calls_create_all_and_dispose(monkeypatch):
    app_main = _load_app(monkeypatch)
    called = {"create_all": False, "dispose": False}

    # Patch Base.metadata.create_all and engine.dispose
    monkeypatch.setattr(
        app_main.Base.metadata, "create_all",
        lambda bind=None: called.__setitem__("create_all", True)
    )
    monkeypatch.setattr(
        app_main.engine, "dispose",
        lambda: called.__setitem__("dispose", True)
    )

    # Trigger FastAPI lifespan
    with TestClient(app_main.app):
        pass

    assert called["create_all"]
    assert called["dispose"]


def test_root_endpoint(monkeypatch):
    app_main = _load_app(monkeypatch)
    with TestClient(app_main.app) as client:
        r = client.get("/")
        assert r.status_code == 200
        assert r.json() == {"message": "FastAPI backend is running!"}


def test_routers_mounted_under_api_prefix(monkeypatch):
    from app.services import asset_services, scan_services, vulnerability_services

    monkeypatch.setattr(asset_services, "list_assets",
                        lambda db, user_id=None: [{"id": 1, "ip_address": "10.0.0.5"}])
    monkeypatch.setattr(scan_services, "list_scans",
                        lambda db, user_id=None: [{"id": 7, "status": "completed", "targets": "127.0.0.1"}])
    monkeypatch.setattr(vulnerability_services, "list_vulnerabilities",
                        lambda db, user_id=None: {"message": "GET/vulnerabilities/ endpoint hit!"})

    def _override_get_db():
        yield object()
    fastapi_app.dependency_overrides[get_db] = _override_get_db

    with TestClient(fastapi_app) as client:
        for path in ["/api/assets/", "/api/scans/", "/api/vulnerabilities/"]:
            r = client.get(path)
            assert r.status_code in (200, 401)


def test_cors_preflight_allows_localhost3000(monkeypatch):
    app_main = _load_app(monkeypatch)
    with TestClient(app_main.app) as client:
        r = client.options(
            "/api/assets/",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert r.headers.get("access-control-allow-origin") == "http://localhost:3000"
