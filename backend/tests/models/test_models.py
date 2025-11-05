# backend/tests/models/test_models.py
from datetime import datetime, UTC
import pytest

from app.models.scan import Scan
from app.models.asset import Asset
from app.models.asset_service import AssetService
from app.models.vulnerability import Vulnerability


def test_create_scan_and_asset_relationship(db_session):
    scan = Scan(status="running", targets="192.168.1.0/24")
    db_session.add(scan)
    db_session.flush()

    asset = Asset(scan_id=scan.id, ip_address="192.168.1.10", hostname="host1", os="linux")
    db_session.add(asset)
    db_session.commit()

    fetched_scan = db_session.get(Scan, scan.id)
    assert fetched_scan is not None
    assert len(fetched_scan.assets) == 1
    assert fetched_scan.assets[0].ip_address == "192.168.1.10"

    fetched_asset = db_session.get(Asset, asset.id)
    assert fetched_asset.scan.id == scan.id
    assert fetched_asset.hostname == "host1"
    assert fetched_asset.os == "linux"


def test_asset_services_and_vulnerabilities_relationships(db_session):
    scan = Scan(status="completed", targets="10.0.0.0/24", finished_at=datetime.now(UTC))
    db_session.add(scan)
    db_session.flush()

    asset = Asset(scan_id=scan.id, ip_address="10.0.0.5", hostname="api", os="ubuntu")
    db_session.add(asset)
    db_session.flush()

    svc = AssetService(asset_id=asset.id, port=443, protocol="tcp",
                       service_name="https", banner="nginx/1.25")
    db_session.add(svc)
    db_session.flush()

    vul = Vulnerability(
        service_id=svc.id,
        template_id="CVE-2023-XXXX",
        severity="high",
        description="TLS misconfiguration",
        evidence="Weak ciphers enabled",
    )
    db_session.add(vul)
    db_session.commit()

    fetched_asset = db_session.get(Asset, asset.id)
    assert len(fetched_asset.services) == 1
    assert fetched_asset.services[0].port == 443

    fetched_svc = db_session.get(AssetService, svc.id)
    assert fetched_svc.asset.id == asset.id
    assert len(fetched_svc.vulnerabilities) == 1
    assert fetched_svc.vulnerabilities[0].template_id == "CVE-2023-XXXX"


def test_cascade_delete_asset_deletes_services_and_vulns(db_session):
    scan = Scan(status="completed", targets="172.16.0.0/24")
    db_session.add(scan)
    db_session.flush()

    asset = Asset(scan_id=scan.id, ip_address="172.16.0.7")
    db_session.add(asset)
    db_session.flush()

    svc1 = AssetService(asset_id=asset.id, port=80, protocol="tcp", service_name="http")
    svc2 = AssetService(asset_id=asset.id, port=22, protocol="tcp", service_name="ssh")
    db_session.add_all([svc1, svc2])
    db_session.flush()

    v1 = Vulnerability(service_id=svc1.id, template_id="Nuclei-001", severity="medium")
    v2 = Vulnerability(service_id=svc2.id, template_id="Nuclei-002", severity="low")
    db_session.add_all([v1, v2])
    db_session.commit()

    db_session.delete(asset)
    db_session.commit()

    assert db_session.get(Asset, asset.id) is None
    assert db_session.get(AssetService, svc1.id) is None
    assert db_session.get(AssetService, svc2.id) is None
    assert db_session.get(Vulnerability, v1.id) is None
    assert db_session.get(Vulnerability, v2.id) is None


def test_cascade_delete_scan_deletes_assets_tree(db_session):
    scan = Scan(status="completed", targets="8.8.8.8")
    db_session.add(scan)
    db_session.flush()

    asset = Asset(scan_id=scan.id, ip_address="8.8.8.8")
    db_session.add(asset)
    db_session.flush()

    svc = AssetService(asset_id=asset.id, port=53, protocol="udp", service_name="dns")
    db_session.add(svc)
    db_session.flush()

    vul = Vulnerability(service_id=svc.id, template_id="DNS-001", severity="info")
    db_session.add(vul)
    db_session.commit()

    db_session.delete(scan)
    db_session.commit()

    assert db_session.get(Scan, scan.id) is None
    assert db_session.get(Asset, asset.id) is None
    assert db_session.get(AssetService, svc.id) is None
    assert db_session.get(Vulnerability, vul.id) is None


@pytest.mark.parametrize(
    "ip,protocol,port",
    [
        ("127.0.0.1", "tcp", 1),
        ("::1", "udp", 65535),
    ],
)
def test_field_bounds_and_types(db_session, ip, protocol, port):
    """Ensure field constraints and types behave correctly."""
    scan = Scan(status="running", targets=ip)
    db_session.add(scan)
    db_session.flush()

    asset = Asset(scan_id=scan.id, ip_address=ip)
    db_session.add(asset)
    db_session.flush()

    svc = AssetService(asset_id=asset.id, port=port, protocol=protocol)
    db_session.add(svc)
    db_session.commit()

    fetched = db_session.get(AssetService, svc.id)
    assert fetched.protocol == protocol
    assert fetched.port == port
    assert fetched.asset.ip_address == ip
