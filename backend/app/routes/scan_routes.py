from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..models.base import get_db
from ..models.scan import Scan
from ..services import scan_services

router = APIRouter(prefix="/scans", tags=["scans"])

class ScanRequest(BaseModel):
    targets: str

@router.get("/summary")
def get_scan_summary(db: Session = Depends(get_db)):
    return scan_services.get_scan_summary(db)

@router.get("")
def list_scans(db: Session = Depends(get_db)):
    return scan_services.list_scans(db)

@router.get("/")
def list_scans_slash(db: Session = Depends(get_db)):
    return scan_services.list_scans(db)

@router.get("/{scan_id}")
def scan_detail(scan_id: int, db: Session = Depends(get_db)):
    scan = scan_services.scan_detail(db, scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan

@router.post("/")
def start_scan(scan_request: ScanRequest, db: Session = Depends(get_db)):
    return scan_services.start_scan(db, scan_request.targets)
