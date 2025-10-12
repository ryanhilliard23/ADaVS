# backend/tests/conftest.py
import os
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

# 1) Point Base to a test DB BEFORE importing your Base/models
os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"

# 2) Import Base and ALL models so metadata knows about every table
from app.models.base import Base  # noqa: E402
from app.models.scan import Scan  # noqa: F401,E402
from app.models.asset import Asset  # noqa: F401,E402
from app.models.asset_service import AssetService  # noqa: F401,E402
from app.models.vulnerability import Vulnerability  # noqa: F401,E402


def _make_engine():
    engine = create_engine(
        os.environ["DATABASE_URL"],
        connect_args={"check_same_thread": False},
        future=True,
        echo=False,
    )

    # Enable FK constraints on SQLite (handy if you rely on ondelete=CASCADE)
    @event.listens_for(engine, "connect")
    def _fk_pragma(dbapi_conn, _):
        cur = dbapi_conn.cursor()
        cur.execute("PRAGMA foreign_keys=ON")
        cur.close()

    return engine


@pytest.fixture(scope="session")
def engine():
    eng = _make_engine()
    # CREATE ALL TABLES ONCE FOR THE TEST SESSION
    Base.metadata.create_all(bind=eng)
    yield eng
    Base.metadata.drop_all(bind=eng)


@pytest.fixture
def db_session(engine):
    """Fresh session per test, bound to the SAME engine used to create tables."""
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    session = SessionLocal()
    try:
        yield session
        session.rollback()
    finally:
        session.close()
