import os
import json
import requests, traceback
from datetime import datetime
from sqlalchemy.orm import Session
from ..models.scan import Scan
from ..models.asset import Asset
from ..models.asset_service import AssetService
from ..utils.nmap_parser import parse_nmap_xml, validate_parsed_data

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

# Takes a target from the frontend and scans it, parses the XML response, and adds info to the DB
def start_scan(db: Session, targets: str):
    print("="*70)
    print("STARTING SCAN (DB MODE)")
    print("="*70)
    print(f"[SCAN] Target: {targets}")

    scan = Scan(status="running", started_at=datetime.now())
    db.add(scan)
    db.commit()
    db.refresh(scan)
    scan_id = scan.id
    print(f"[SCAN] Created scan ID: {scan_id}")

    try:
        print(f"[SCAN] Sending request to VPS: {VPS_SCANNER_URL}/scan")
        response = requests.post(
            f"{VPS_SCANNER_URL}/scan",
            json={"targets": [targets]},
            headers={"X-Scanner-Token": SCANNER_TOKEN},
            timeout=600  
        )

        print(f"[SCAN] VPS response status: {response.status_code}")
        if response.status_code != 200:
            raise RuntimeError(f"VPS returned {response.status_code}: {response.text[:200]}")

        xml_output = response.json().get("xml", "")
        if not xml_output:
            raise RuntimeError("No XML data received from VPS scanner")

        print(f"[SCAN] Received {len(xml_output)} bytes of XML")

        hosts = parse_nmap_xml(xml_output)
        if not validate_parsed_data(hosts):
            raise RuntimeError("Parsed data invalid or empty")

        print(f"[SCAN] Parsed {len(hosts)} host(s)")

        assets_created = assets_updated = services_created = services_updated = 0

        for h in hosts:
            ip = h["ip_address"]
            hostname = h.get("hostname")
            os_name = h.get("os")

            asset = db.query(Asset).filter(Asset.ip_address == ip).first()
            if asset:
                asset.hostname = hostname
                asset.os = os_name
                asset.scan_id = scan_id
                assets_updated += 1
            else:
                asset = Asset(
                    scan_id=scan_id,
                    ip_address=ip,
                    hostname=hostname,
                    os=os_name
                )
                db.add(asset)
                db.flush()
                assets_created += 1

            for s in h.get("services", []):
                port, proto = s["port"], s["protocol"]
                svc = (
                    db.query(AssetService)
                    .filter_by(asset_id=asset.id, port=port, protocol=proto)
                    .first()
                )
                if svc:
                    svc.service_name = s.get("service_name")
                    svc.banner = s.get("banner")
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

        print("="*70)
        print("SCAN COMPLETE")
        print("="*70)
        print(f"✓ Hosts discovered: {len(hosts)}")
        print(f"✓ Assets created:   {assets_created}")
        print(f"✓ Assets updated:   {assets_updated}")
        print(f"✓ Services created: {services_created}")
        print(f"✓ Services updated: {services_updated}")

        return {
            "scan_id": scan_id,
            "status": "completed",
            "target": targets,
            "hosts_discovered": len(hosts),
            "assets_created": assets_created,
            "assets_updated": assets_updated,
            "services_created": services_created,
            "services_updated": services_updated,
            "message": "Scan completed successfully",
        }

    except Exception as e:
        traceback.print_exc()
        scan.status = "failed"
        scan.finished_at = datetime.now()
        db.commit()
        return {"scan_id": scan_id, "status": "failed", "error": str(e)}
