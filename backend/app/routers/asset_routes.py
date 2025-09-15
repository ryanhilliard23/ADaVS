from fastapi import APIRouter

router = APIRouter()

@router.get("/assets")
def list_assets():
    # Call the service function (currently a placeholder/dummy)
    return [
        {
            "id": 1,
            "ip_address": "192.168.1.2",
            "hostname": "host1",
            "os": "Linux",
            "open_ports": [22, 80],
            "last_seen": "2025-09-15T02:48:50"
        }
    ]

@router.get("/assets/{asset_id}")
def get_asset(asset_id: int):
    # Call the service function (currently a placeholder/dummy)
    return {
        "id": asset_id,
        "services": [
            {"port_number": 22, "protocol": "tcp", "service_name": "ssh", "version": "OpenSSH 8.2"},
            {"port_number": 80, "protocol": "tcp", "service_name": "http", "version": "Apache 2.4"}
        ],
        "vulnerabilities": [
            {"id": 101, "name": "CVE-2023-12345", "severity": "critical", "target": "192.168.1.2", "detected_at": "2025-09-15T02:48:50"}
        ]
    }

@router.get("/vulnerabilities")
def list_vulnerabilities(severity: str = None):
    # Call service function (placeholder/dummy)
    vulns = [
        {"id": 101, "name": "CVE-2023-12345", "severity": "critical", "target": "192.168.1.2", "detected_at": "2025-09-15T02:48:50"},
        {"id": 102, "name": "CVE-2023-56789", "severity": "medium", "target": "192.168.1.3", "detected_at": "2025-09-15T02:48:50"},
    ]
    if severity:
        vulns = [v for v in vulns if v["severity"] == severity]
    return vulns

@router.get("/vulnerabilities/{vuln_id}")
def get_vulnerability(vuln_id: int):
    # Call service function (placeholder/dummy)
    return {
        "id": vuln_id,
        "cve_id": f"CVE-2023-{vuln_id}",
        "affected_host": "192.168.1.2",
        "affected_port": 22,
        "description": "Sample vulnerability description"
    }