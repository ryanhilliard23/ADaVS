import os
import requests
import traceback
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from ..models.scan import Scan
from ..models.asset import Asset
from ..models.asset_service import AssetService
from ..utils.nmap_parser import parse_nmap_xml, validate_parsed_data
from ..utils.nuclei_runner import run_nuclei_scan
from ..public_scanning.recon_service import discover_domain_assets

VPS_SCANNER_URL = os.getenv("VPS_SCANNER_URL")
SCANNER_TOKEN = os.getenv("SCANNER_TOKEN")

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

def start_scan(db: Session, targets: str, user_id: int, scan_type: str):
    active_scan = db.query(Scan).filter(
        Scan.user_id == user_id,
        Scan.status == "running"
    ).first()

    if active_scan:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="You already have a scan in progress. Please wait for it to finish."
        )
    
    print("="*70)
    print(f"STARTING SCAN ({scan_type.upper()} MODE)")
    print(f"[SCAN] Target: {targets}")
    print("="*70)

    scan = Scan(status="running", started_at=datetime.now(), targets=targets, user_id=user_id)
    db.add(scan)
    db.commit()
    db.refresh(scan)
    scan_id = scan.id

    try:
        result_data = {}

        # PRIVATE SCAN (Active Nmap + Nuclei)
        if scan_type == 'private':
            print(f"[SCAN] Private mode: Initiating Active Nmap Scan on VPS...")
            
            response= requests.post(
                f"{VPS_SCANNER_URL}/scan",
                json={"targets": [targets]},
                headers={"X-Scanner-Token": SCANNER_TOKEN},
                timeout=600
            )

            if response.status_code != 200:
                raise RuntimeError(f"VPS returned {response.status_code}: {response.text[:200]}")

            xml_output = response.json().get("xml", "")
            if not xml_output:
                raise RuntimeError("No XML data received from VPS scanner")

            hosts = parse_nmap_xml(xml_output)
            if not validate_parsed_data(hosts):
                raise RuntimeError("Parsed data invalid or empty")

            assets_created = assets_updated = services_created = services_updated = 0
            
            existing_assets = {
                a.ip_address: a
                for a in db.query(Asset).join(Scan).filter(
                    Asset.ip_address.in_([h["ip_address"] for h in hosts]),
                    Scan.user_id == user_id
                ).all()
            }

            for h in hosts:
                ip = h["ip_address"]
                hostname = h.get("hostname")
                os_name = h.get("os")

                asset = existing_assets.get(ip)
                if asset:
                    asset.hostname = hostname
                    asset.os = os_name
                    asset.scan_id = scan_id
                    assets_updated += 1
                else:
                    asset = Asset(scan_id=scan_id, ip_address=ip, hostname=hostname, os=os_name)
                    db.add(asset)
                    db.flush()
                    existing_assets[ip] = asset
                    assets_created += 1

                for s in h.get("services", []):
                    port, proto = s["port"], s["protocol"]
                    svc = db.query(AssetService).filter_by(asset_id=asset.id, port=port, protocol=proto).first()
                    if svc:
                        svc.service_name = s.get("service_name")
                        svc.banner = s.get("banner")
                        services_updated += 1
                    else:
                        svc = AssetService(
                            asset_id=asset.id, port=port, protocol=proto,
                            service_name=s.get("service_name"), banner=s.get("banner")
                        )
                        db.add(svc)
                        services_created += 1

            db.commit()

            ips = [h["ip_address"] for h in hosts if "ip_address" in h]
            print(f"[SCAN] Triggering Nuclei scan for {len(ips)} host(s)")
            try:
                nuclei_result = run_nuclei_scan(db, scan_id, ips)
                print("[SCAN] Nuclei scan completed:", nuclei_result)
            except Exception as e:
                print("[SCAN] Nuclei scan failed:", e)

            result_data = {
                "hosts_discovered": len(hosts),
                "assets_created": assets_created,
                "services_created": services_created
            }

        # PUBLIC SCAN
        elif scan_type == 'public':
            print(f"[SCAN] Public mode: Utilizing OSINT tools (Shodan/Censys)...")
            
            hosts = discover_domain_assets(targets) 

            if not hosts:
                print("[SCAN] No assets found via OSINT.")
                scan.status = "completed"
                scan.finished_at = datetime.now()
                db.commit()
                return {
                    "scan_id": scan_id,
                    "status": "completed",
                    "target": targets,
                    "hosts_discovered": 0,
                    "message": "No assets discovered via OSINT sources",
                }

            assets_created = assets_updated = services_created = services_updated = 0

            existing_assets = {
                a.ip_address: a
                for a in db.query(Asset).join(Scan).filter(
                    Asset.ip_address.in_([h["ip_address"] for h in hosts]),
                    Scan.user_id == user_id
                ).all()
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
                    svc = db.query(AssetService).filter_by(asset_id=asset.id, port=port, protocol=proto).first()
                    
                    if svc:
                        if s.get("service_name"): svc.service_name = s["service_name"]
                        if s.get("banner"): svc.banner = s["banner"]
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
            
            result_data = {
                "hosts_discovered": len(hosts),
                "assets_created": assets_created,
                "services_created": services_created
            }

        scan.status = "completed"
        scan.finished_at = datetime.now()
        db.commit()

        return {
            "scan_id": scan_id,
            "status": "completed",
            "scan_type": scan_type,
            "target": targets,
            **result_data,
            "message": "Scan completed successfully",
        }

    except Exception as e:
        traceback.print_exc()
        scan.status = "failed"
        scan.finished_at = datetime.now()
        db.commit()
        return {"scan_id": scan_id, "status": "failed", "error": str(e)}
