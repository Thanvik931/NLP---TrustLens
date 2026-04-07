"""
Dataset routes:
  POST /api/datasets/upload      multipart CSV upload
  GET  /api/datasets             list all datasets
  GET  /api/datasets/{id}        single dataset detail
  GET  /api/datasets/{id}/profile  profiling report
"""

import json
import os
import shutil
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import Dataset, User
from app.db.session import get_db
from app.middleware.auth import get_current_user
from app.schemas.dataset import DatasetOut, DatasetProfile
from app.services.profiling import profile_dataset

router = APIRouter(prefix="/api/datasets", tags=["datasets"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _dataset_to_out(ds: Dataset) -> DatasetOut:
    return DatasetOut(
        id=str(ds.id),
        name=ds.name,
        domain=ds.domain,
        description=ds.description,
        file_path=ds.file_path,
        row_count=ds.row_count,
        feature_count=ds.feature_count,
        sensitive_cols=ds.sensitive_cols or [],
        target_col=ds.target_col,
        created_at=ds.created_at.isoformat(),
    )


def _get_dataset_or_404(dataset_id: str, db: Session) -> Dataset:
    try:
        uid = uuid.UUID(dataset_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid dataset ID format")

    ds = db.query(Dataset).filter(Dataset.id == uid).first()
    if not ds:
        raise HTTPException(status_code=404, detail=f"Dataset {dataset_id} not found")
    return ds


# ---------------------------------------------------------------------------
# POST /api/datasets/upload
# ---------------------------------------------------------------------------

@router.post("/upload", response_model=DatasetOut, status_code=201)
async def upload_dataset(
    file: UploadFile = File(...),
    name: str = Form(...),
    domain: str = Form(...),
    description: Optional[str] = Form(None),
    sensitive_cols: Optional[str] = Form(None),   # JSON array string e.g. '["sex","race"]'
    target_col: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload a CSV dataset file.
    sensitive_cols: JSON-encoded list, e.g. '["sex","race"]'
    """
    # Validate file type
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are accepted",
        )

    # Parse sensitive_cols from JSON string → Python list
    parsed_sensitive: List[str] = []
    if sensitive_cols:
        try:
            parsed_sensitive = json.loads(sensitive_cols)
            if not isinstance(parsed_sensitive, list):
                raise ValueError
        except (json.JSONDecodeError, ValueError):
            raise HTTPException(
                status_code=400,
                detail="sensitive_cols must be a valid JSON array, e.g. '[\"sex\",\"race\"]'",
            )

    # Save file to disk
    os.makedirs(settings.DATASET_DIR, exist_ok=True)
    safe_name = f"{uuid.uuid4()}_{file.filename}"
    dest = os.path.join(settings.DATASET_DIR, safe_name)

    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Quick row/feature count using pandas (import inline to keep startup fast)
    import pandas as pd
    try:
        df_head = pd.read_csv(dest, low_memory=False)
        row_count = len(df_head)
        feature_count = len(df_head.columns)
    except Exception as exc:
        os.remove(dest)
        raise HTTPException(status_code=400, detail=f"Could not parse CSV: {exc}")

    # Save to DB
    dataset = Dataset(
        name=name,
        domain=domain,
        description=description,
        file_path=dest,
        row_count=row_count,
        feature_count=feature_count,
        sensitive_cols=parsed_sensitive,
        target_col=target_col,
        created_by=current_user.id,
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)

    return _dataset_to_out(dataset)


# ---------------------------------------------------------------------------
# GET /api/datasets
# ---------------------------------------------------------------------------

@router.get("", response_model=List[DatasetOut])
def list_datasets(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return paginated list of all datasets."""
    datasets = db.query(Dataset).order_by(Dataset.created_at.desc()).offset(skip).limit(limit).all()
    return [_dataset_to_out(ds) for ds in datasets]


# ---------------------------------------------------------------------------
# GET /api/datasets/{id}
# ---------------------------------------------------------------------------

@router.get("/{dataset_id}", response_model=DatasetOut)
def get_dataset(
    dataset_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return a single dataset by ID."""
    return _dataset_to_out(_get_dataset_or_404(dataset_id, db))


# ---------------------------------------------------------------------------
# GET /api/datasets/{id}/profile
# ---------------------------------------------------------------------------

@router.get("/{dataset_id}/profile", response_model=DatasetProfile)
def get_dataset_profile(
    dataset_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Run profiling on the stored CSV and return:
      - Per-column stats
      - Cohort size counts per sensitive column
      - Missing value heatmap
      - Correlation matrix
      - Proxy variable warnings
    """
    ds = _get_dataset_or_404(dataset_id, db)

    if not ds.file_path or not os.path.exists(ds.file_path):
        raise HTTPException(
            status_code=404,
            detail="Dataset file not found on server. Re-upload the CSV.",
        )

    try:
        report = profile_dataset(
            dataset_id=dataset_id,
            file_path=ds.file_path,
            sensitive_cols=ds.sensitive_cols or [],
            target_col=ds.target_col,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Profiling failed: {exc}")

    return report
