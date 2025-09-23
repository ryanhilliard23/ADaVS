from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

# File for the database
DATABASE_URL = "sqlite:///./adavs.db"

# SQLite connection
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# Foreign Key functionality
@event.listens_for(engine, "connect")
def _fk_pragma_on_connect(dbapi_conn, _):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.close()

# Used for database operations
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()