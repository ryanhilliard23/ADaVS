from sqlalchemy import text
from sqlalchemy.orm import Session

def wake_db_up(db: Session):
    """
    Ensures the Neon database is awake and connection is valid.
    Safe to call before long insert or update operations.
    """
    try:
        db.execute(text("SELECT 1"))
        db.commit()
        print("[DB] DB connection verified and awake.")
    except Exception as e:
        print(f"[DB] DB likely suspended. Reconnecting... ({e})")
        db.rollback()
        try:
            db.execute(text("SELECT 1"))
            db.commit()
            print("[DB] Reconnected successfully.")
        except Exception as err:
            print(f"[DB] Failed to reconnect to DB: {err}")
            raise