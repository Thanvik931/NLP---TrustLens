"""Governance Rule routes."""
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.models import GovernanceRule, MLModel, User
from app.db.session import get_db
from app.middleware.auth import get_current_user
from app.schemas.governance import GovernanceRuleCreate, GovernanceRuleUpdate, GovernanceRuleOut

router = APIRouter(prefix="/api/governance", tags=["governance"])

def _rule_to_out(r: GovernanceRule) -> GovernanceRuleOut:
    return GovernanceRuleOut(
        id=str(r.id), model_id=str(r.model_id), name=r.name, description=r.description,
        category=r.category, threshold=r.threshold, metric=r.metric, is_active=r.is_active
    )

@router.post("", response_model=GovernanceRuleOut, status_code=status.HTTP_201_CREATED)
def create_rule(
    rule_in: GovernanceRuleCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new Governance Rule for a model."""
    try:
        model_uuid = uuid.UUID(rule_in.model_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid model_id format")
        
    model = db.query(MLModel).filter(MLModel.id == model_uuid).first()
    if not model:
        raise HTTPException(status_code=404, detail="MLModel not found")

    r = GovernanceRule(
        model_id=model_uuid, name=rule_in.name, description=rule_in.description,
        category=rule_in.category, threshold=rule_in.threshold, metric=rule_in.metric,
        is_active=rule_in.is_active
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    return _rule_to_out(r)

@router.get("/model/{model_id}", response_model=List[GovernanceRuleOut])
def get_rules_for_model(
    model_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all governance rules associated with a specific model."""
    try:
        muuid = uuid.UUID(model_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid model_id format")
    
    rs = db.query(GovernanceRule).filter(GovernanceRule.model_id == muuid).all()
    return [_rule_to_out(r) for r in rs]

@router.put("/{rule_id}", response_model=GovernanceRuleOut)
def update_rule(
    rule_id: str, 
    rule_in: GovernanceRuleUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a governance rule's settings or threshold."""
    try:
        ruuid = uuid.UUID(rule_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid rule_id format")
    
    r = db.query(GovernanceRule).filter(GovernanceRule.id == ruuid).first()
    if not r:
        raise HTTPException(status_code=404, detail="Governance Rule not found")
    
    update_data = rule_in.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(r, k, v)
        
    db.commit()
    db.refresh(r)
    return _rule_to_out(r)
