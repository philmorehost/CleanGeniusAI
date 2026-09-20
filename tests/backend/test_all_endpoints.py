import os
import sys
import time
import json
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src/backend')))

os.environ["MOCK_WINDOWS"] = "true"
os.environ["MOCK_AI"] = "true"

from main import app, db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_system_info(client):
    res = client.get('/api/system/info')
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert "total_space_gb" in data["data"]

def test_fast_scan_and_cleanup_flow(client):
    # 1. Start Fast Scan with max_files limit for fast test execution
    res = client.post('/api/scan/start', json={"mode": "fast", "options": {"find_duplicates": True, "ai_analysis": True, "max_files": 50}})
    assert res.status_code == 200
    scan_id = res.get_json()["scan_id"]

    # 2. Poll Scan Status with extended timeout for CI runners
    completed = False
    for _ in range(100):
        time.sleep(0.2)
        s_res = client.get(f'/api/scan/{scan_id}')
        s_data = s_res.get_json()
        assert s_data["success"] is True
        if s_data["status"] == "completed":
            completed = True
            break

    assert completed is True

    # 3. Start Cleanup
    c_res = client.post('/api/cleanup/start', json={"scan_id": scan_id, "options": {"recycle_bin": True}})
    assert c_res.status_code == 200
    cleanup_id = c_res.get_json()["cleanup_id"]

    # 4. Poll Cleanup Status
    c_completed = False
    cl_data = {}
    for _ in range(250):
        time.sleep(0.2)
        cl_res = client.get(f'/api/cleanup/{cleanup_id}')
        cl_data = cl_res.get_json()
        assert cl_data["success"] is True
        if cl_data["status"] == "completed":
            c_completed = True
            break
        elif cl_data["status"] == "failed":
            pytest.fail(f"Cleanup worker failed: {cl_data.get('error') or cl_data.get('message')}")

    assert c_completed is True, f"Cleanup timed out before completing: {cl_data}"

def test_registry_scan_and_dashboard(client):
    r_res = client.post('/api/scan/start', json={"mode": "registry"})
    assert r_res.status_code == 200
    scan_id = r_res.get_json()["scan_id"]

    for _ in range(100):
        time.sleep(0.2)
        st = client.get(f'/api/scan/{scan_id}').get_json()
        if st["status"] == "completed":
            break

    dash = client.get('/api/dashboard').get_json()
    assert dash["success"] is True
    assert "health_score" in dash["data"]

def test_ai_test_and_providers(client):
    prov = client.get('/api/ai/providers').get_json()
    assert prov["success"] is True
    assert len(prov["providers"]) >= 5

    t_res = client.get('/api/ai/test/deepseek').get_json()
    assert t_res["success"] is True
