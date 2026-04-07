"""
test_model_cards.py
=========================
Standalone test for Model Card generation (PDF).
Run with: .venv\\Scripts\\python test_model_cards.py
"""

import sys
import os
import requests

sys.path.insert(0, os.path.dirname(__file__))

BASE_URL = "http://localhost:8000"
DIVIDER = "=" * 60

def main():
    print(f"\n{DIVIDER}")
    print("  TrustLens AI - Model Card Generation Test")
    print(DIVIDER)

    # 1. Login to get a token
    login_data = {"email": "check2@trustlens.ai", "password": "Test123!"}
    res = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    assert res.status_code == 200
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("  [OK] Logged in successfully")

    # 2. Get an existing Audit (from Task 9)
    # Actually wait, we need an audit ID. Let's trigger one if needed or just query datasets/models.
    # To be safe, let's just trigger a new audit so we 100% have one.
    
    res = requests.get(f"{BASE_URL}/api/datasets?skip=0&limit=1", headers=headers)
    assert res.status_code == 200
    datasets = res.json()
    if not datasets:
        print("  [X] No datasets found. Run Task 3.")
        sys.exit(1)
    dataset_id = datasets[0]["id"]

    res = requests.get(f"{BASE_URL}/api/models", headers=headers)
    assert res.status_code == 200
    models = res.json()
    if not models:
        print("  [X] No ML models. Run Task 8.")
        sys.exit(1)
    model_id = models[0]["id"]

    print("\n  Triggering Audit to attach Model Card to...")
    audit_res = requests.post(
        f"{BASE_URL}/api/audits/trigger", 
        json={"dataset_id": dataset_id, "model_id": model_id}, 
        headers=headers
    )
    assert audit_res.status_code == 201
    audit_id = audit_res.json()["id"]
    print(f"  [OK] New Audit ID: {audit_id}")

    # 3. Create Model Card
    card_data = {
        "audit_id": audit_id,
        "intended_use": "Predict whether a loan should be approved based on historic data.",
        "out_of_scope_use": "Not suitable for predictive policing or automated sentencing.",
        "training_data_desc": "UCI Adult Dataset.",
        "evaluation_data": "10% held-out test set.",
        "limitations": "Model exhibits higher false positive rates for young adults.",
        "recommendations": "Use with human-in-the-loop oversight."
    }

    print("\n  Generating Model Card (JSON + PDF)...")
    res_card = requests.post(f"{BASE_URL}/api/model_cards", json=card_data, headers=headers)
    assert res_card.status_code == 201, f"Model Card creation failed: {res_card.text}"
    card = res_card.json()
    print(f"  [OK] Model Card Generated! ID: {card['id']}")
    print(f"  [OK] Attached to Audit: {card['audit_id']}")

    # 4. Fetch JSON representation
    res_get = requests.get(f"{BASE_URL}/api/model_cards/audit/{audit_id}", headers=headers)
    assert res_get.status_code == 200
    print(f"  [OK] Model Card JSON retrieved.")

    # 5. Download PDF
    print("\n  Downloading PDF Version...")
    res_pdf = requests.get(f"{BASE_URL}/api/model_cards/audit/{audit_id}/pdf", headers=headers)
    assert res_pdf.status_code == 200, f"PDF fetch failed: {res_pdf.text}"
    assert res_pdf.headers['Content-Type'] == 'application/pdf'
    
    # Save the file locally just to prove it worked
    pdf_path = "test_downloaded_model_card.pdf"
    with open(pdf_path, 'wb') as f:
        f.write(res_pdf.content)

    print(f"  [OK] PDF downloaded successfully! Saved locally as: {pdf_path}")
    print(f"       File size: {os.path.getsize(pdf_path)} bytes")

    print(f"\n{DIVIDER}")
    print("  ALL ASSERTIONS PASSED - Task 10 complete! [OK]")
    print(DIVIDER + "\n")

if __name__ == '__main__':
    main()
