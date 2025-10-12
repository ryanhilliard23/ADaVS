from app.models.asset import Asset

def test_asset_model_fields():
    asset = Asset()
    assert hasattr(asset, "id")
    assert hasattr(asset, "ip_address")
    assert hasattr(asset, "hostname")
    assert hasattr(asset, "os")