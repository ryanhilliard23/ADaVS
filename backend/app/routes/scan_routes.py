from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from pydantic import BaseModel
from ..models.base import get_db
from ..models.scan import Scan
from ..services import scan_services
from ..services import user_services

router = APIRouter(prefix="/scans", tags=["scans"])

class ScanRequest(BaseModel):
    targets: str
    scan_type: str = "private"

# Returns all scans in the database.
@router.get("/", response_model=list[dict])
def list_scans(
    db: Session = Depends(get_db),
    current_user: dict = Depends(user_services.get_current_user)
):
    result = db.execute(
        select(
            Scan.id,
            Scan.targets,
            Scan.status,
            Scan.started_at,
            Scan.finished_at,
        )
        .where(Scan.user_id == current_user['user_id'])
        .order_by(Scan.started_at.desc())
    ).all()

    return [
        {
            "id": row.id,
            "targets": row.targets,
            "status": row.status,
            "started_at": row.started_at,
            "finished_at": row.finished_at,
        }
        for row in result
    ]


# Returns a specific scan from the database.
@router.get("/{scan_id}")
def scan_detail(scan_id: int, db: Session = Depends(get_db)):
    scan = scan_services.scan_detail(db, scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan


# Starts a new scan: sends an input to scan with nmap/shodan depending on type, XML is parsed, and info is stored in DB
@router.post("/")
def start_scan(scan_request: ScanRequest, db: Session = Depends(get_db), current_user: dict = Depends(user_services.get_current_user)):
    return scan_services.start_scan(
        db, 
        scan_request.targets, 
        current_user['user_id'], 
        scan_request.scan_type
    )