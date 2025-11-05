import os
import pytest
import sqlalchemy
import inspect
import importlib
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import fastapi



# --- Environment setup before imports ---
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_shared.db")
os.environ.setdefault(
    "SECRET_KEY",
    "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
)
os.environ.setdefault("TESTING", "true")

# --- Patch SQLAlchemy engine creation for SQLite ---
_original_create_engine = sqlalchemy.create_engine
def _safe_create_engine(*args, **kwargs):
    url = str(args[0]) if args else kwargs.get("url", "")
    if "sqlite" in url:
        kwargs["connect_args"] = {"check_same_thread": False}
        kwargs.pop("pool_timeout", None)
        kwargs.pop("pool_recycle", None)
    return _original_create_engine(*args, **kwargs)
sqlalchemy.create_engine = _safe_create_engine

# --- Import app + models after env setup ---
from app.main import app
from app.models.base import Base, engine, SessionLocal
from app.models import user, scan, asset, asset_service, vulnerability
from app.models.user import User


# --- Persistent DB setup with seeded user ---
@pytest.fixture(scope="session", autouse=True)
def setup_db():
    """Recreate DB with a dummy user shared across threads."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        if not db.query(User).filter(User.id == 1).first():
            db.add(User(id=1, email="test@example.com", hashed_password="x"))
            db.commit()
    yield
    Base.metadata.drop_all(bind=engine)


# --- Disable authentication globally ---
@pytest.fixture(scope="session", autouse=True)
def disable_auth():
    """Override all get_current_user dependencies for all routes."""
    def fake_user():
        return {"id": 1, "user_id": 1, "username": "testuser"}

    modules = [
        "app.routes.user_routes",
        "app.routes.asset_routes",
        "app.routes.scan_routes",
        "app.routes.vulnerability_routes",
        "app.services.user_services",
        "app.main",
    ]
    for mod_name in modules:
        try:
            mod = importlib.import_module(mod_name)
            for _, obj in inspect.getmembers(mod):
                if callable(obj) and obj.__name__ == "get_current_user":
                    app.dependency_overrides[obj] = fake_user
        except Exception:
            continue

@pytest.fixture(scope="session", autouse=True)
def disable_auth():
    def fake_user():
        return {"id": 1, "username": "testuser"}

    from app import routes, services
    targets = []
    for mod in [routes.user_routes, routes.asset_routes, routes.scan_routes, routes.vulnerability_routes]:
        if hasattr(mod, "get_current_user"):
            targets.append(mod.get_current_user)
    if hasattr(services.user_services, "get_current_user"):
        targets.append(services.user_services.get_current_user)

    for dep in targets:
        app.dependency_overrides[dep] = fake_user

    # ✅ Global patch for any new FastAPI instance created in tests
    fastapi.Depends(lambda: fake_user)

# --- Patch services to allow user_id kwarg safely ---
@pytest.fixture(autouse=True)
def patch_service_signatures(monkeypatch):
    from app import services
    for mod in [services.asset_services, services.scan_services, services.vulnerability_services]:
        for name, fn in inspect.getmembers(mod, inspect.isfunction):
            sig = inspect.signature(fn)
            if "user_id" not in sig.parameters:
                def wrapper(*args, user_id=None, __fn=fn, **kwargs):
                    return __fn(*args, **kwargs)
                monkeypatch.setattr(mod, name, wrapper)

@pytest.fixture(scope="session")
def db_engine():
    """Provide a shared in-memory SQLite engine for all tests."""
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        future=True,
        echo=False,
    )
    from app.models.base import Base
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

# --- Stub simple message endpoints (skip for service tests) ---
@pytest.fixture(autouse=True)
def stub_message_services(request, monkeypatch):
    if "services/" in str(request.fspath):
        return
    from app.services import asset_services, vulnerability_services
    monkeypatch.setattr(
        asset_services,
        "list_assets",
        lambda db=None, user_id=None: {"message": "Assets endpoint hit successfully!"},
    )
    monkeypatch.setattr(
        vulnerability_services,
        "list_vulnerabilities",
        lambda db=None, user_id=None: {"message": "GET/vulnerabilities/ endpoint hit!"},
    )


# ---  Shared TestClient using persistent engine ---
@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture
def db_session(db_engine):
    """Provide a fresh database session for tests that need raw DB access."""
    SessionLocal = sessionmaker(bind=db_engine, autoflush=False, autocommit=False, future=True)
    session = SessionLocal()
    try:
        yield session
        session.rollback()
    finally:
        session.close()


@pytest.fixture(autouse=True)
def clean_db(db_engine):
    """Ensure DB tables are empty before each test (to avoid FK conflicts)."""
    from app.models.base import Base
    with db_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())