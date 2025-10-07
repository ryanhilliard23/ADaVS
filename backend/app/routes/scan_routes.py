from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..models.base import get_db
from ..services import scan_services

router = APIRouter(prefix="/scans", tags=["scans"])

class ScanRequest(BaseModel):
    targets: str

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

# Starts a new scan: sends an input to scan with nmap, XML is parsed, and info is stored in DB
@router.post("/")
def start_scan(scan_request: ScanRequest, db: Session = Depends(get_db)):
    return scan_services.start_scan(db, scan_request.targets)
