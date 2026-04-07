"""Model Cards routes."""
import uuid
import os
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.db.models import ModelCard, AuditRun, MLModel, User
from app.db.session import get_db
from app.middleware.auth import get_current_user
from app.schemas.model_cards import ModelCardCreate, ModelCardOut
from app.services.pdf_generator import generate_model_card_pdf

router = APIRouter(prefix="/api/model_cards", tags=["model_cards"])

def _card_to_out(c: ModelCard) -> ModelCardOut:
    return ModelCardOut(
        id=str(c.id),
        audit_id=str(c.audit_id),
        model_name=c.model_name,
        intended_use=c.intended_use,
        out_of_scope_use=c.out_of_scope_use,
        training_data_desc=c.training_data_desc,
        evaluation_data=c.evaluation_data,
        performance_summary=c.performance_summary,
        fairness_summary=c.fairness_summary,
        limitations=c.limitations,
        recommendations=c.recommendations,
        generated_at=c.generated_at
    )

@router.post("", response_model=ModelCardOut, status_code=status.HTTP_201_CREATED)
def create_model_card(
    card_in: ModelCardCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate and store a new Model Card for a given Audit Run."""
    try:
        a_uuid = uuid.UUID(card_in.audit_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid audit_id format")

    audit = db.query(AuditRun).filter(AuditRun.id == a_uuid).first()
    if not audit:
        raise HTTPException(status_code=404, detail="AuditRun not found")

    # If exists, block creation (1:1 relation)
    existing = db.query(ModelCard).filter(ModelCard.audit_id == a_uuid).first()
    if existing:
        raise HTTPException(status_code=400, detail="Model Card already exists for this audit")

    # Merge audit data with provided input
    model = db.query(MLModel).filter(MLModel.id == audit.model_id).first()
    
    # Prep data for DB and PDF
    card = ModelCard(
        audit_id=a_uuid,
        model_name=card_in.model_name or (model.name if model else "Unknown"),
        intended_use=card_in.intended_use,
        out_of_scope_use=card_in.out_of_scope_use,
        training_data_desc=card_in.training_data_desc,
        evaluation_data=card_in.evaluation_data,
        performance_summary=card_in.performance_summary or {
            "overall_accuracy": audit.overall_accuracy
        },
        fairness_summary=card_in.fairness_summary or {
            "demographic_parity": audit.demographic_parity,
            "disparate_impact": audit.disparate_impact,
            "equalized_odds_tpr": audit.equalized_odds_tpr
        },
        limitations=card_in.limitations,
        recommendations=card_in.recommendations
    )
    
    db.add(card)
    db.commit()
    db.refresh(card)

    # Generate PDF
    card_dict = {
        "model_name": card.model_name,
        "intended_use": card.intended_use,
        "out_of_scope_use": card.out_of_scope_use,
        "training_data_desc": card.training_data_desc,
        "evaluation_data": card.evaluation_data,
        "limitations": card.limitations,
        "recommendations": card.recommendations,
        "performance_summary": card.performance_summary,
        "fairness_summary": card.fairness_summary
    }
    
    pdf_path = generate_model_card_pdf(card_dict, output_dir="app/static/reports")
    
    # Store path on AuditRun or just keep it on disk (Since task only mentions DB/PDF).
    # For now, we will store the path on audit
    audit.audit_report_path = pdf_path
    db.commit()

    return _card_to_out(card)


@router.get("/audit/{audit_id}", response_model=ModelCardOut)
def get_model_card_by_audit(
    audit_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve the JSON details of a model card by its Audit ID."""
    try:
        a_uuid = uuid.UUID(audit_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid audit_id format")

    card = db.query(ModelCard).filter(ModelCard.audit_id == a_uuid).first()
    if not card:
        raise HTTPException(status_code=404, detail="Model Card not found")
        
    return _card_to_out(card)


@router.get("/audit/{audit_id}/pdf")
def download_model_card_pdf(
    audit_id: str, 
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user) # Optionally require auth
):
    """Download the generated PDF Model Card for a given Audit Run."""
    try:
        a_uuid = uuid.UUID(audit_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid audit_id format")

    audit = db.query(AuditRun).filter(AuditRun.id == a_uuid).first()
    if not audit or not audit.audit_report_path:
        raise HTTPException(status_code=404, detail="PDF not generated or Audit not found")
        
    if not os.path.exists(audit.audit_report_path):
        raise HTTPException(status_code=404, detail="PDF file missing from disk")

    return FileResponse(
        path=audit.audit_report_path,
        media_type="application/pdf",
        filename=os.path.basename(audit.audit_report_path)
    )
