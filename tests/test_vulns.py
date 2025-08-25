from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_add_vuln_and_list_with_min_severity():
    # create asset
    r = client.post("/assets", json={"name": "srv-2"})
    assert r.status_code == 201
    asset_id = r.json()["id"]

    # add multiple vulns
    v1 = {"cve_id": "CVE-2024-0001", "severity": "low"}
    v2 = {"cve_id": "CVE-2024-0002", "severity": "high"}
    v3 = {"cve_id": "CVE-2024-0003", "severity": "critical"}

    for v in (v1, v2, v3):
        rr = client.post(f"/vulns/assets/{asset_id}", json=v)
        assert rr.status_code == 201, rr.text

    # list without filter
    r = client.get(f"/vulns/assets/{asset_id}")
    assert r.status_code == 200
    all_v = r.json()
    assert len(all_v) == 3

    # min_severity=high -> expect high + critical
    r = client.get(f"/vulns/assets/{asset_id}?min_severity=high")
    assert r.status_code == 200
    filtered = r.json()
    assert {v["severity"] for v in filtered} == {"high", "critical"}


def test_duplicate_vuln_for_asset_409():
    r = client.post("/assets", json={"name": "srv-3"})
    asset_id = r.json()["id"]

    v = {"cve_id": "CVE-2024-1111", "severity": "medium"}
    r1 = client.post(f"/vulns/assets/{asset_id}", json=v)
    r2 = client.post(f"/vulns/assets/{asset_id}", json=v)
    assert r1.status_code == 201
    assert r2.status_code == 409


def test_vuln_summary_counts():
    # Not asserting exact totals (suite order), just structure and keys
    r = client.get("/vulns/summary")
    assert r.status_code == 200
    data = r.json()
    assert "counts" in data
    for k in ["low", "medium", "high", "critical"]:
        assert k in data["counts"]
