from sqlalchemy.orm import Session
from app.models.asset_model import Asset, Vulnerability

def get_assets(db: Session, scan_id: int = None):
    query = db.query(Asset)
    return query.all()

def get_asset_by_id(db: Session, asset_id: int):
    return db.query(Asset).filter(Asset.id == asset_id).first()

def get_vulnerabilities(db: Session, severity: str = None):
    query = db.query(Vulnerability)
    if severity:
        query = query.filter(Vulnerability.severity == severity)
    return query.all()

def get_vulnerability_by_id(db: Session, vuln_id: int):
    return db.query(Vulnerability).filter(Vulnerability.id == vuln_id).first()