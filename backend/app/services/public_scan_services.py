from datetime import datetime
from typing import List, Dict

from sqlalchemy.orm import Session

from ..models.scan import Scan
from ..models.asset import Asset
from ..models.asset_service import AssetService

from ..public_scanning.recon_service import discover_domain_assets


def start_public_scan(db: Session, domain: str, user_id: int):
    domain = domain.lower().strip()

    scan = Scan(
        status="running",
        started_at=datetime.now(),
        targets=domain,
        user_id=user_id,
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)
    scan_id = scan.id

    try:
        hosts: List[Dict] = discover_domain_assets(domain)

        if not hosts:
            scan.status = "completed"
            scan.finished_at = datetime.now()
            db.commit()
            return {
                "scan_id": scan_id,
                "status": "completed",
                "target": domain,
                "hosts_discovered": 0,
                "assets_created": 0,
                "assets_updated": 0,
                "services_created": 0,
                "services_updated": 0,
                "message": "No assets discovered via OSINT sources",
            }

        assets_created = assets_updated = services_created = services_updated = 0

        existing_assets = {
            a.ip_address: a
            for a in db.query(Asset)
            .join(Scan)
            .filter(
                Asset.ip_address.in_([h["ip_address"] for h in hosts]),
                Scan.user_id == user_id,
            )
            .all()
        }

        for h in hosts:
            ip = h["ip_address"]
            hostname = h.get("hostname")
            os_name = h.get("os")

            asset = existing_assets.get(ip)
            if asset:
                asset.hostname = hostname or asset.hostname
                asset.os = os_name or asset.os
                asset.scan_id = scan_id
                assets_updated += 1
            else:
                asset = Asset(
                    scan_id=scan_id,
                    ip_address=ip,
                    hostname=hostname,
                    os=os_name,
                )
                db.add(asset)
                db.flush()
                existing_assets[ip] = asset
                assets_created += 1

            for s in h.get("services", []):
                port, proto = s["port"], s["protocol"]
                svc = (
                    db.query(AssetService)
                    .filter_by(asset_id=asset.id, port=port, protocol=proto)
                    .first()
                )
                if svc:
                    if s.get("service_name"):
                        svc.service_name = s["service_name"]
                    if s.get("banner"):
                        svc.banner = s["banner"]
                    services_updated += 1
                else:
                    svc = AssetService(
                        asset_id=asset.id,
                        port=port,
                        protocol=proto,
                        service_name=s.get("service_name"),
                        banner=s.get("banner"),
                    )
                    db.add(svc)
                    services_created += 1

        scan.status = "completed"
        scan.finished_at = datetime.now()
        db.commit()

        return {
            "scan_id": scan_id,
            "status": "completed",
            "target": domain,
            "hosts_discovered": len(hosts),
            "assets_created": assets_created,
            "assets_updated": assets_updated,
            "services_created": services_created,
            "services_updated": services_updated,
            "message": "Public passive scan completed successfully",
        }

    except Exception as e:
        scan.status = "failed"
        scan.finished_at = datetime.now()
        db.commit()
        return {"scan_id": scan_id, "status": "failed", "error": str(e)}
