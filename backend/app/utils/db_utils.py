from sqlalchemy import text
from sqlalchemy.orm import Session

def wake_db_up(db: Session):
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