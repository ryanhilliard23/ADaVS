from app.services.asset_services import list_assets, asset_detail

class DummyDB:
    pass  # Replace with a mock or fixture if needed

def test_list_assets_returns_message():
    db = DummyDB()
    result = list_assets(db)
    assert "message" in result

def test_asset_detail_returns_message():
    db = DummyDB()
    result = asset_detail(db, 1)
    assert "message" in result or result is None