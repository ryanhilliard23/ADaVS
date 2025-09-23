from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..models.base import get_db
from ..services import scan_services

router = APIRouter(prefix="/scans", tags=["scans"])

# Returns all scans in the database.
@router.get("/")
def list_scans(db: Session = Depends(get_db)):
    return scan_services.list_scans(db)

# Returns a specific scan from the database.
@router.get("/{scan_id}")
def scan_detail(scan_id: int, db: Session = Depends(get_db)):
    scan = scan_services.scan_detail(db, scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan

# Starts a new scan (not implemented yet).
@router.post("/")
def start_scan(target: str, db: Session = Depends(get_db)):
    return scan_services.start_scan(db, target)
