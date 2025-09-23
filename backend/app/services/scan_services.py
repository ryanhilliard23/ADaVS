from sqlalchemy.orm import Session
from ..models.scan import Scan

# Returns all scans from the database and their information.
def list_scans(db: Session):
    scans = db.query(Scan).all()
    return [
        {
            "id": scan.id,
            "started_at": scan.started_at,
            "finished_at": scan.finished_at,
            "status": scan.status,
        }
        for scan in scans
    ]

# Returns details of a single scan from the database.
def scan_detail(db: Session, scan_id: int):
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        return None

    return {
        "id": scan.id,
        "started_at": scan.started_at,
        "finished_at": scan.finished_at,
        "status": scan.status,
        "assets": [
            {
                "id": asset.id,
                "ip_address": asset.ip_address,
                "hostname": asset.hostname,
                "os": asset.os,
            }
            for asset in scan.assets
        ],
    }

# Placeholder for now.
def start_scan(db: Session, target: str):
    return {"message": f"Scan requested for target: {target}"}
