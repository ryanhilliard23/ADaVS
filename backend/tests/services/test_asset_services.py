# backend/tests/services/test_asset_services.py
from app.models.scan import Scan
from app.models.asset import Asset
from app.models.asset_service import AssetService
from app.models.vulnerability import Vulnerability
from app.services import asset_services

def test_list_assets_stub_message(db_session):
    # current implementation returns a stub message
    assert asset_services.list_assets(db_session) == {"message": "Assets endpoint hit successfully!"}

def test_asset_detail_not_found(db_session):
    assert asset_services.asset_detail(db_session, 999) is None

def test_asset_detail_happy_path(db_session):
    # create a scan, asset, service, vulnerability
    scan = Scan(status="completed", targets="10.0.0.0/24")
    db_session.add(scan); db_session.flush()

    asset = Asset(scan_id=scan.id, ip_address="10.0.0.5", hostname="api", os="ubuntu")
    db_session.add(asset); db_session.flush()

    svc = AssetService(asset_id=asset.id, port=443, protocol="tcp", service_name="https", banner="nginx")
    db_session.add(svc); db_session.flush()

    vul = Vulnerability(service_id=svc.id, template_id="TLS-001", severity="high", description="TLS issue", evidence="weak ciphers")
    db_session.add(vul); db_session.commit()

    out = asset_services.asset_detail(db_session, asset.id)
    assert out["id"] == asset.id
    assert out["ip_address"] == "10.0.0.5"
    assert len(out["services"]) == 1
    assert out["services"][0]["port"] == 443
    assert len(out["services"][0]["vulnerabilities"]) == 1
    assert out["services"][0]["vulnerabilities"][0]["template_id"] == "TLS-001"
