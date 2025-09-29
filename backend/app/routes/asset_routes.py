from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..models.base import get_db
from ..services import asset_services

router = APIRouter(prefix="/assets", tags=["assets"])

# Returns all assets in the database.
@router.get("/")
def list_assets(db: Session = Depends(get_db)):
    return asset_services.list_assets(db)

# Returns a specific asset
@router.get("/{asset_id}")
def asset_detail(asset_id: int, db: Session = Depends(get_db)):
    #asset = asset_services.asset_detail(db, asset_id)
    #if not asset:
    #    raise HTTPException(status_code=404, detail="Asset not found")
    #return asset
    return {"message": f"Asset {asset_id} endpoint hit successfully!"}