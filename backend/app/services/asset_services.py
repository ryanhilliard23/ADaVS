from sqlalchemy.orm import Session
from ..models.asset import Asset
from ..models.asset_service import AssetService
from ..models.scan import Scan

# Returns a list of all assets from the database.
def list_assets(db: Session, user_id: int):
    assets = (db.query(Asset).join(Scan).filter(Scan.user_id == user_id).all())
    return [
       {
           "id": asset.id,
           "ip_address": asset.ip_address,
           "hostname": asset.hostname,
           "os": asset.os,
           "services": [
            {
                "id": service.id,
                "port": service.port,
                "protocol": service.protocol,
                "service_name": service.service_name,
                "banner": service.banner,
            }
            for service in asset.services  # Asset → AssetService relationship
           ]
       }
       for asset in assets
    ]
    

# Returns a single asset from the database.
def asset_detail(db: Session, asset_id: int):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        return None

    return {
        "id": asset.id,
        "ip_address": asset.ip_address,
        "hostname": asset.hostname,
        "os": asset.os,
        "services": [
            {
                "id": service.id,
                "port": service.port,
                "protocol": service.protocol,
                "service_name": service.service_name,
                "banner": service.banner,
                "vulnerabilities": [
                    {
                        "id": vuln.id,
                        "template_id": vuln.template_id,
                        "severity": vuln.severity,
                        "description": vuln.description,
                        "evidence": vuln.evidence,
                    }
                    for vuln in service.vulnerabilities
                ],
            }
            for service in asset.services  # Asset → AssetService relationship
        ],
    }