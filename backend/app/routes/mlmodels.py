"""MLModel routes."""
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.models import MLModel, User
from app.db.session import get_db
from app.middleware.auth import get_current_user
from app.schemas.mlmodel import MLModelCreate, MLModelOut

router = APIRouter(prefix="/api/models", tags=["models"])

def _mlmodel_to_out(m: MLModel) -> MLModelOut:
    return MLModelOut(
        id=str(m.id), name=m.name, framework=m.framework, domain=m.domain,
        description=m.description, model_file=m.model_file, is_active=m.is_active,
        created_at=m.created_at.isoformat()
    )

@router.post("", response_model=MLModelOut, status_code=status.HTTP_201_CREATED)
def create_model(
    model_in: MLModelCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Register a new MLModel."""
    m = MLModel(**model_in.model_dump())
    db.add(m)
    db.commit()
    db.refresh(m)
    return _mlmodel_to_out(m)

@router.get("", response_model=List[MLModelOut])
def list_models(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all registered ML models."""
    ms = db.query(MLModel).order_by(MLModel.created_at.desc()).all()
    return [_mlmodel_to_out(m) for m in ms]

@router.get("/{model_id}", response_model=MLModelOut)
def get_model(
    model_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a single MLModel by ID."""
    try:
        muid = uuid.UUID(model_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid model_id format")
    
    m = db.query(MLModel).filter(MLModel.id == muid).first()
    if not m:
        raise HTTPException(status_code=404, detail="MLModel not found")
    return _mlmodel_to_out(m)
