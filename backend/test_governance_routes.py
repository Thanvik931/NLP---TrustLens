"""
test_governance_routes.py
=========================
Standalone test for the TrustLens Governance endpoints.
Run with: .venv\\Scripts\\python test_governance_routes.py
"""

import sys
import os
import requests
import uuid

sys.path.insert(0, os.path.dirname(__file__))

BASE_URL = "http://localhost:8000"
DIVIDER = "=" * 60

def main():
    print(f"\n{DIVIDER}")
    print("  TrustLens AI - MLModels & Governance API Test")
    print(DIVIDER)

    # 1. Login to get a token
    login_data = {"email": "check2@trustlens.ai", "password": "Test123!"}
    res = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    
    if res.status_code == 401:
        # User not found, try to register
        register_data = {"email": "check2@trustlens.ai", "password": "Test123!", "role": "ADMIN"}
        res = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
        res = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)

    assert res.status_code == 200, f"Login failed: {res.text}"
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("  [OK] Logged in successfully")

    # 2. Create an MLModel
    model_data = {
        "name": "Credit Risk Predictor",
        "framework": "scikit-learn",
        "domain": "finance",
        "description": "Predicts default risk for loan applicants."
    }
    print("\n  Creating MLModel...")
    res = requests.post(f"{BASE_URL}/api/models", json=model_data, headers=headers)
    assert res.status_code == 201, f"Failed to create MLModel: {res.text}"
    model_id = res.json()["id"]
    print(f"  [OK] MLModel created with ID: {model_id}")

    # 3. Create Governance Rules for the Model
    rule_data_dp = {
        "model_id": model_id,
        "name": "Demographic Parity Check",
        "category": "fairness",
        "threshold": 0.1,
        "metric": "demographic_parity"
    }
    rule_data_di = {
        "model_id": model_id,
        "name": "Disparate Impact Ratio Check",
        "category": "fairness",
        "threshold": 0.8,
        "metric": "disparate_impact"
    }
    
    print("\n  Creating Governance Rules...")
    res_dp = requests.post(f"{BASE_URL}/api/governance", json=rule_data_dp, headers=headers)
    assert res_dp.status_code == 201, f"Failed to create DP Rule: {res_dp.text}"
    rule_id_dp = res_dp.json()["id"]
    print(f"  [OK] DP Rule created: {rule_id_dp}")

    res_di = requests.post(f"{BASE_URL}/api/governance", json=rule_data_di, headers=headers)
    assert res_di.status_code == 201, f"Failed to create DI Rule: {res_di.text}"
    print(f"  [OK] DI Rule created")

    # 4. Get Rules for the Model
    print("\n  Fetching Rules for the MLModel...")
    res = requests.get(f"{BASE_URL}/api/governance/model/{model_id}", headers=headers)
    assert res.status_code == 200
    rules = res.json()
    assert len(rules) == 2, f"Expected 2 rules, got {len(rules)}"
    print(f"  [OK] Retrieved {len(rules)} rules for model")

    # 5. Update a Rule
    print("\n  Updating DP Rule Threshold...")
    update_data = {"threshold": 0.05}
    res = requests.put(f"{BASE_URL}/api/governance/{rule_id_dp}", json=update_data, headers=headers)
    assert res.status_code == 200
    assert res.json()["threshold"] == 0.05, "Threshold was not updated"
    print("  [OK] Rule threshold updated successfully")

    print(f"\n{DIVIDER}")
    print("  ALL ASSERTIONS PASSED - Task 8 complete! [OK]")
    print(DIVIDER + "\n")

if __name__ == '__main__':
    main()
