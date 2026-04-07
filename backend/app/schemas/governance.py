"""Pydantic schemas for GovernanceRule."""
from typing import Optional, List
from pydantic import BaseModel

class GovernanceRuleCreate(BaseModel):
    model_id: str
    name: str
    description: Optional[str] = None
    category: str      # fairness | legal | safety | explainability
    threshold: Optional[float] = None
    metric: Optional[str] = None
    is_active: bool = True

class GovernanceRuleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    threshold: Optional[float] = None
    metric: Optional[str] = None
    is_active: Optional[bool] = None

class GovernanceRuleOut(BaseModel):
    id: str
    model_id: str
    name: str
    description: Optional[str]
    category: str
    threshold: Optional[float]
    metric: Optional[str]
    is_active: bool

    model_config = {"from_attributes": True}
