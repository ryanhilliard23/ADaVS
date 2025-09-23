# app/api/routes/scan_routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.scan_service import create_scan, get_scans, get_scan_by_id, get_assets_by_scan, get_vulnerabilities_by_scan

router = APIRouter()

@router.post("/scan")
def start_scan(target: str, db: Session = Depends(get_db)):
    pass
@router.get("/scans")
def list_scans(db: Session = Depends(get_db)):
   pass
@router.get("/scans/{scan_id}")
def get_scan(scan_id: int, db: Session = Depends(get_db)):
    pass
