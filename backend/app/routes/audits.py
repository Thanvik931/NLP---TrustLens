"""Audit routes."""
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.models import AuditRun, AuditStatus, Dataset, MLModel, User
from app.db.session import get_db
from app.middleware.auth import get_current_user
from app.schemas.audits import AuditTriggerRequest, AuditRunOut
from app.worker import run_full_audit_task

router = APIRouter(prefix="/api/audits", tags=["audits"])

def _audit_to_out(a: AuditRun) -> AuditRunOut:
    return AuditRunOut(
        id=str(a.id),
        dataset_id=str(a.dataset_id),
        model_id=str(a.model_id),
        triggered_by=str(a.triggered_by) if a.triggered_by else None,
        status=a.status.value if hasattr(a.status, 'value') else a.status,
        progress=a.progress,
        demographic_parity=a.demographic_parity,
        equalized_odds_tpr=a.equalized_odds_tpr,
        equalized_odds_fpr=a.equalized_odds_fpr,
        disparate_impact=a.disparate_impact,
        overall_accuracy=a.overall_accuracy,
        started_at=a.started_at,
        completed_at=a.completed_at
    )

@router.post("/trigger", response_model=AuditRunOut, status_code=status.HTTP_201_CREATED)
def trigger_audit(
    request: AuditTriggerRequest, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Trigger a new background audit run for a given dataset and model."""
    try:
        ds_uuid = uuid.UUID(request.dataset_id)
        mod_uuid = uuid.UUID(request.model_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")

    # Verify dataset & model exist
    dataset = db.query(Dataset).filter(Dataset.id == ds_uuid).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
        
    model = db.query(MLModel).filter(MLModel.id == mod_uuid).first()
    if not model:
        raise HTTPException(status_code=404, detail="MLModel not found")

    # Create new AuditRun record
    audit_run = AuditRun(
        dataset_id=ds_uuid,
        model_id=mod_uuid,
        triggered_by=current_user.id,
        status=AuditStatus.RUNNING,
        progress=0
    )
    db.add(audit_run)
    db.commit()
    db.refresh(audit_run)

    # Trigger Celery Background Task
    task = run_full_audit_task.delay(str(audit_run.id))
    
    # Store celery task id back in DB
    audit_run.celery_task_id = task.id
    db.commit()
    db.refresh(audit_run)

    return _audit_to_out(audit_run)

@router.get("", response_model=List[AuditRunOut])
def list_all_audits(
    skip: int = 0, 
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all audit runs."""
    audits = db.query(AuditRun).order_by(AuditRun.started_at.desc()).offset(skip).limit(limit).all()
    return [_audit_to_out(a) for a in audits]

@router.get("/{audit_id}", response_model=AuditRunOut)
def get_audit_status(
    audit_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the current status and metrics of a running or completed audit."""
    try:
        a_uuid = uuid.UUID(audit_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid audit_id format")
        
    audit = db.query(AuditRun).filter(AuditRun.id == a_uuid).first()
    if not audit:
        raise HTTPException(status_code=404, detail="AuditRun not found")
        
    return _audit_to_out(audit)
