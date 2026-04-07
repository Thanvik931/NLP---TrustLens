# TrustLens AI 🛡️

**TrustLens AI** is an enterprise-grade AI Governance and Explainability Platform designed to audit machine learning models for algorithmic bias, enforce fairness thresholds, and automatically generate regulatory compliance PDF Model Cards.

![TrustLens UI](https://img.shields.io/badge/Streamlit-UI-FF4B4B.svg)
![FastAPI Backend](https://img.shields.io/badge/FastAPI-Backend-009688.svg)
![Celery Orchestration](https://img.shields.io/badge/Celery-Orchestration-37814A.svg)

## 🚀 Key Features

* **End-to-End Governance Orchestration**: Pair active Pandas datasets with Machine Learning frameworks in the UI to trigger deep asynchronous fairness audits.
* **Interactive Dashboard**: A highly polished, robust, dark-mode Streamlit multi-tab interface.
* **Fairness & Bias Engineering**: Integrated with Microsoft's `fairlearn`, utilizing Demographic Parity, Disparate Impact, and Equalized Odds natively.
* **Algorithmic Explainability**: Runs actual `RandomForestClassifiers` underneath the hood, plotting mathematical non-linear dependencies via SHAP / LIME combinations.
* **Compliance Ready**: One-click generation of beautifully formatted PDF documents outlining model specifications, deployment limitations, and mitigation recommendations utilizing `reportlab`.

## 🏗️ System Architecture

The platform runs on a robust microservices infrastructure:

1. **Streamlit**: Python frontend interface (`localhost:8501`).
2. **FastAPI**: Blisteringly fast API connecting algorithms to the UI (`localhost:8000`).
3. **Celery Worker**: Asynchronous background jobs tackling heavy-duty model inferences and matrix operations.
4. **PostgreSQL**: Stores relational integrity data (Users, Auth, Audits, ML Models, Datasets).
5. **Redis**: Cache and message broker for Celery queues.

## 🛠️ Local Environment Setup

### 1. Prerequisites
Ensure you have Python 3.12+ and Docker Desktop installed on your machine.

### 2. Boot the Databases
Navigate to the root directory and start the background infrastructure:
```bash
docker-compose up -d
```
*(This launches PostgreSQL on port `5433` and Redis on port `6379`)*

### 3. Start the Backend API
Open a new terminal tab and fire up the FastAPI backend:
```powershell
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Boot the Celery ML Workers
Open a second terminal to handle the heavy AI lifting:
```powershell
cd backend
python -m celery -A app.worker.celery_app worker --loglevel=info --pool=solo
```

### 5. Launch the Dashboard
Open a final terminal to render the frontend Streamlit UI:
```powershell
cd frontend
python -m streamlit run app.py --server.port 8501 --server.headless true
```

Navigate your browser to [http://localhost:8501](http://localhost:8501).

## 📄 License

This project is licensed under the [MIT License](LICENSE).
