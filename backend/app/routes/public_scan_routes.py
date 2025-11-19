from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..models.base import get_db
from ..services import user_services, public_scan_services


router = APIRouter(prefix="/public-scans", tags=["public-scans"])


class PublicScanRequest(BaseModel):
    domain: str


@router.post("/")
def start_public_scan(
    scan_request: PublicScanRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(user_services.get_current_user),
):
    return public_scan_services.start_public_scan(
        db=db,
        domain=scan_request.domain.strip(),
        user_id=current_user["user_id"],
    )
