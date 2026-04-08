import requests
import streamlit as st
import os

BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
if BASE_URL and not BASE_URL.startswith("http"):
    BASE_URL = f"https://{BASE_URL}"

def get_headers():
    headers = {"Content-Type": "application/json"}
    if "access_token" in st.session_state:
        headers["Authorization"] = f"Bearer {st.session_state['access_token']}"
    return headers

def ping_health():
    """Check if the FastAPI backend is running."""
    try:
        res = requests.get(f"{BASE_URL}/health", timeout=2)
        return res.status_code == 200
    except requests.exceptions.ConnectionError:
        return False

def login(email, password):
    res = requests.post(f"{BASE_URL}/api/auth/login", json={"email": email, "password": password})
    return res

def register(email, password, role="VIEWER"):
    res = requests.post(f"{BASE_URL}/api/auth/register", json={"email": email, "password": password, "role": role})
    return res

def fetch_datasets():
    return requests.get(f"{BASE_URL}/api/datasets", headers=get_headers())

def get_dataset_profile(dataset_id):
    return requests.get(f"{BASE_URL}/api/datasets/{dataset_id}/profile", headers=get_headers())

def fetch_models():
    return requests.get(f"{BASE_URL}/api/models", headers=get_headers())

def create_model(payload):
    return requests.post(f"{BASE_URL}/api/models", json=payload, headers=get_headers())

def fetch_rules(model_id):
    return requests.get(f"{BASE_URL}/api/governance/model/{model_id}", headers=get_headers())

def create_rule(payload):
    return requests.post(f"{BASE_URL}/api/governance", json=payload, headers=get_headers())

def trigger_audit(dataset_id, model_id):
    payload = {"dataset_id": dataset_id, "model_id": model_id}
    return requests.post(f"{BASE_URL}/api/audits/trigger", json=payload, headers=get_headers())

def get_audit_status(audit_id):
    return requests.get(f"{BASE_URL}/api/audits/{audit_id}", headers=get_headers())

def fetch_audits():
    return requests.get(f"{BASE_URL}/api/audits", headers=get_headers())

def get_model_card(audit_id):
    return requests.get(f"{BASE_URL}/api/model_cards/audit/{audit_id}", headers=get_headers())

def get_model_card_pdf(audit_id):
    return requests.get(f"{BASE_URL}/api/model_cards/audit/{audit_id}/pdf", headers=get_headers(), stream=True)
