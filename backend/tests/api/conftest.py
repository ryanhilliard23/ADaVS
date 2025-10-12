# backend/tests/api/conftest.py
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

# use an in-memory sqlite db for routes, too
os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"

from app.models.base import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402

def _engine():
    eng = create_engine(
        os.environ["DATABASE_URL"],
        connect_args={"check_same_thread": False},
        future=True,
    )

    @event.listens_for(eng, "connect")
    def _fk_on(dbapi_conn, _):
        cur = dbapi_conn.cursor()
        cur.execute("PRAGMA foreign_keys=ON")
        cur.close()

    return eng

@pytest.fixture(scope="session")
def engine():
    eng = _engine()
    Base.metadata.create_all(bind=eng)
    yield eng
    Base.metadata.drop_all(bind=eng)

@pytest.fixture
def db_session(engine):
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    s = Session()
    try:
        yield s
        s.rollback()
    finally:
        s.close()

@pytest.fixture
def client(db_session):
    # override the app's DB dependency to use our test session
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
