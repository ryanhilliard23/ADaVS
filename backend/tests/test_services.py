def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_assets_list(client):
    response = client.get("/api/assets/")
    assert response.status_code == 200
    assert "message" in response.json() or isinstance(response.json(), list)

def test_asset_detail(client):
    response = client.get("/api/assets/1")
    assert response.status_code in [200, 404]