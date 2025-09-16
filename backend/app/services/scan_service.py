# app/crud/scan_crud.py
from sqlalchemy.orm import Session
from app.models.scan_model import Scan, Asset, Vulnerability
from datetime import datetime

def create_scan(db: Session, target: str):
    scan = Scan(
        target=target,
        status="queued",
        assets_found=0,
        started_at=datetime.utcnow(),
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)
    return scan

def get_scans(db: Session):
    return db.query(Scan).order_by(Scan.started_at.desc()).all()

def get_scan_by_id(db: Session, scan_id: int):
    return db.query(Scan).filter(Scan.id == scan_id).first()

def get_assets_by_scan(db: Session, scan_id: int):
    return db.query(Asset).filter(Asset.scan_id == scan_id).all()

def get_vulnerabilities_by_scan(db: Session, scan_id: int):
    return db.query(Vulnerability).filter(Vulnerability.scan_id == scan_id).all()
