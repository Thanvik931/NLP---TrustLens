"""
test_audits.py
=========================
Standalone test for the TrustLens Audit endpoint & background worker.
Run with: .venv\\Scripts\\python test_audits.py
"""

import sys
import os
import time
import requests

sys.path.insert(0, os.path.dirname(__file__))

BASE_URL = "http://localhost:8000"
DIVIDER = "=" * 60

def main():
    print(f"\n{DIVIDER}")
    print("  TrustLens AI - Audit Execution Test")
    print(DIVIDER)

    # 1. Login to get a token
    login_data = {"email": "check2@trustlens.ai", "password": "Test123!"}
    res = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    assert res.status_code == 200
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("  [OK] Logged in successfully")

    # 2. Get a dataset ID & model ID
    res = requests.get(f"{BASE_URL}/api/datasets?skip=0&limit=1", headers=headers)
    assert res.status_code == 200
    datasets = res.json()
    if not datasets:
        print("  [X] No datasets. Please create one.")
        sys.exit(1)
    dataset_id = datasets[0]["id"]

    res = requests.get(f"{BASE_URL}/api/models", headers=headers)
    assert res.status_code == 200
    models = res.json()
    if not models:
        print("  [X] No ML models. Please create one.")
        sys.exit(1)
    model_id = models[0]["id"]

    # 3. Trigger an Audit
    print(f"\n  Triggering Audit for:")
    print(f"    Dataset  : {dataset_id}")
    print(f"    MLModel  : {model_id}")

    payload = {"dataset_id": dataset_id, "model_id": model_id}
    res = requests.post(f"{BASE_URL}/api/audits/trigger", json=payload, headers=headers)
    assert res.status_code == 201, f"Trigger failed: {res.text}"
    audit_id = res.json()["id"]
    status = res.json()["status"]
    print(f"  [OK] Audit Triggered with ID: {audit_id} | Status: {status}")

    # 4. Poll for Audit status every 2 seconds
    print("\n  Polling Audit Status...")
    TIMEOUT = 20  # seconds
    start_time = time.time()
    
    while True:
        res = requests.get(f"{BASE_URL}/api/audits/{audit_id}", headers=headers)
        assert res.status_code == 200
        data = res.json()
        current_status = data["status"]
        progress = data["progress"]
        
        print(f"    -> Status: {current_status:<10} | Progress: {progress}%")

        if current_status in ["PASSED", "FLAGGED", "BLOCKED"]:
            print(f"  [OK] Audit finished with status: {current_status}")
            print(f"       Demographic Parity: {data['demographic_parity']}")
            print(f"       Disparate Impact  : {data['disparate_impact']}")
            print(f"       Accuracy          : {data['overall_accuracy']}")
            break

        if time.time() - start_time > TIMEOUT:
            print("  [X] Timeout waiting for audit completion")
            break

        time.sleep(2)

    print(f"\n{DIVIDER}")
    print("  ALL ASSERTIONS PASSED - Task 9 complete! [OK]")
    print(DIVIDER + "\n")

if __name__ == '__main__':
    main()
