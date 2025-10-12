# backend/tests/services/conftest.py
import os
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from app.models.base import Base

# use a safe in-memory DB for service tests
os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"

from app.models.base import Base  # noqa: E402
from app.models.scan import Scan  # noqa: F401,E402
from app.models.asset import Asset  # noqa: F401,E402
from app.models.asset_service import AssetService  # noqa: F401,E402
from app.models.vulnerability import Vulnerability  # noqa: F401,E402

def _engine():
    eng = create_engine(
        os.environ["DATABASE_URL"],
        connect_args={"check_same_thread": False},
        future=True,
        echo=False,
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

@pytest.fixture(autouse=True)
def _clean_db(engine):
    """
    Ensure a pristine database before every test.
    Deletes from child tables first to satisfy FKs.
    """
    with engine.begin() as conn:
        # fast & FK-safe: delete in reverse dependency order
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())