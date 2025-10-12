# backend/tests/test_main.py
import importlib
import types
import pytest

from starlette.testclient import TestClient


def _load_app(monkeypatch):
    """
    Load app.main after setting DATABASE_URL. We reload to ensure
    each test sees a fresh module state for monkeypatches.
    """
    monkeypatch.setenv("DATABASE_URL", "sqlite+pysqlite:///:memory:")
    import app.main as app_main
    importlib.reload(app_main)
    return app_main


def test_lifespan_calls_create_all_and_dispose(monkeypatch):
    app_main = _load_app(monkeypatch)

    called = {"create_all": False, "dispose": False}

    # Patch the methods used inside lifespan
    monkeypatch.setattr(
        app_main.Base.metadata, "create_all",
        lambda bind=None: called.__setitem__("create_all", True)
    )
    monkeypatch.setattr(
        app_main.engine, "dispose",
        lambda: called.__setitem__("dispose", True)
    )

    # Trigger startup/shutdown
    with TestClient(app_main.app):
        pass

    assert called["create_all"] is True
    assert called["dispose"] is True


def test_root_and_test_endpoints(monkeypatch):
    app_main = _load_app(monkeypatch)
    with TestClient(app_main.app) as client:
        r = client.get("/")
        assert r.status_code == 200
        assert r.json() == {"message": "FastAPI backend is running!"}

        r2 = client.get("/test")
        assert r2.status_code == 200
        assert r2.json() == {"message": "Communication successful."}


def test_routers_mounted_under_api_prefix(monkeypatch):
    app_main = _load_app(monkeypatch)

    # Monkeypatch services to avoid real DB work
    from app.services import asset_services, scan_services, vulnerability_services

    monkeypatch.setattr(
        asset_services, "list_assets",
        lambda db: [{"id": 1, "ip_address": "10.0.0.5"}]
    )
    monkeypatch.setattr(
        scan_services, "list_scans",
        lambda db: [{"id": 7, "status": "completed", "targets": "127.0.0.1"}]
    )
    # vuln list is stubbed in the route to return a message, so no patch needed

    # Override get_db dependency to yield a harmless object
    from app.models.base import get_db
    def _override_get_db():
        yield object()
    app_main.app.dependency_overrides[get_db] = _override_get_db

    with TestClient(app_main.app) as client:
        a = client.get("/api/assets/")
        assert a.status_code == 200
        assert a.json() == [{"id": 1, "ip_address": "10.0.0.5"}]

        s = client.get("/api/scans/")
        assert s.status_code == 200
        assert s.json() == [{"id": 7, "status": "completed", "targets": "127.0.0.1"}]

        v = client.get("/api/vulnerabilities/")
        assert v.status_code == 200
        assert v.json() == {"message": "GET/vulnerabilities/ endpoint hit!"}

    app_main.app.dependency_overrides.clear()


def test_cors_preflight_allows_localhost3000(monkeypatch):
    app_main = _load_app(monkeypatch)
    with TestClient(app_main.app) as client:
        # CORS preflight for GET /api/assets/
        r = client.options(
            "/api/assets/",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        # Starlette may return 200 or 204; we only check header presence
        assert r.headers.get("access-control-allow-origin") == "http://localhost:3000"
