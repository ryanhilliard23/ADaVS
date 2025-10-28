import os
import requests
import json
from typing import List
from datetime import datetime
from sqlalchemy.orm import Session
from ..models.asset import Asset
from ..models.asset_service import AssetService
from ..models.vulnerability import Vulnerability
from ..utils.db_utils import wake_db_up

NUCLEI_URL = os.getenv("VPS_NUCLEI_URL")
NUCLEI_TOKEN = os.getenv("NUCLEI_TOKEN")


def run_nuclei_scan(db: Session, scan_id: int, ips: List[str]):
    print("=" * 70)
    print(f"RUNNING NUCLEI VULNERABILITY SCAN FOR SCAN ID {scan_id}")
    print(f"Using IPs from Nmap run: {ips}")
    print("=" * 70)

    print("DEBUGGING 2")

    services = (
        db.query(AssetService)
        .join(Asset)
        .filter(Asset.ip_address.in_(ips))
        .order_by(Asset.ip_address, AssetService.port)
        .all()
    )

    print("DEBUGGING 3")
    print(services)

    print(f"[NUCLEI] Found {len(services)} total services")

    if not services:
        print("[NUCLEI] No services found for provided IPs.")
        return {"status": "no_targets", "targets": [], "services_count": 0}

    targets_payload = []
    for svc in services:
        ip = svc.asset.ip_address
        port = svc.port
        tag = (svc.service_name or "network").strip().lower()

        targets_payload.append({
            "target": f"{ip}:{port}",
            "tags": tag
        })

    payload = {"targets": targets_payload}

    print("DEBUGGING 4")
    print(payload)

    try:
        response = requests.post(
            f"{NUCLEI_URL}/scan",
            headers={"X-Scanner-Token": NUCLEI_TOKEN},
            json=payload,
            timeout=None,
        )
        print(f"[NUCLEI] Runner response: {response.status_code}")
        response.raise_for_status()
        nuclei_results = response.json()

        print("DEBUGGING 6")
        print(nuclei_results)

        if not isinstance(nuclei_results, list):
            print("[NUCLEI] Unexpected JSON from runner:", nuclei_results)
            nuclei_results = []

        wake_db_up(db)
        services = [db.merge(svc) for svc in services]
        db.flush()

    except Exception as e:
        print(f"[NUCLEI] Error during unified scan:", e)
        return {"status": "failed", "error": str(e)}

    inserted = 0
    for result in nuclei_results:  
        try:
            template_id = result.get("template-id") or result.get("templateID")
            info = result.get("info", {})
            severity = info.get("severity") or result.get("severity") or "unknown"
            description = (
                info.get("name")
                or info.get("description")
                or template_id
                or "nuclei-finding"
            )
            matched = (
                result.get("matched-at")
                or result.get("matched_at")
                or result.get("url")
                or ""
            )

            matched_service = None
            for svc in services:
                if f"{svc.asset.ip_address}:{svc.port}" in matched:
                    matched_service = svc
                    break

            if not matched_service:
                print("[NUCLEI] Could not match finding to service, skipping:", template_id, matched[:120])
                continue

            vuln = Vulnerability(
                service_id=matched_service.id,
                template_id=(template_id[:255] if template_id else None),
                severity=severity,
                description=description,
                evidence=matched[:255],
            )
            db.add(vuln)
            inserted += 1
        except Exception as e:
            print(f"[NUCLEI] Error processing result: {e}")

    db.commit()

    print(f"[NUCLEI] Inserted {inserted} vulnerabilities for scan {scan_id}")
    print("=" * 70)
    print("NUCLEI SCAN COMPLETE")
    print("=" * 70)

    return {
        "status": "ok",
        "inserted": inserted,
        "targets": len(targets_payload),
        "services_scanned": len(services),
    }
