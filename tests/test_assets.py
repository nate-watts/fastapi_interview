from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_create_and_get_asset():
    r = client.post(
        "/assets", json={"name": "srv-1", "owner": "alice", "tags": ["prod", "db"]}
    )
    assert r.status_code == 201, r.text
    asset = r.json()
    assert asset["name"] == "srv-1"
    assert sorted(asset["tags"]) == ["db", "prod"]

    rid = asset["id"]
    r = client.get(f"/assets/{rid}")
    assert r.status_code == 200
    assert r.json()["id"] == rid


def test_duplicate_asset_name_409():
    client.post("/assets", json={"name": "srv-dup"})
    r = client.post("/assets", json={"name": "srv-dup"})
    assert r.status_code == 409
