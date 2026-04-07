"""Pydantic schemas for Model Cards."""
from typing import Optional, Any, Dict
from pydantic import BaseModel
from datetime import datetime

class ModelCardCreate(BaseModel):
    audit_id: str
    model_name: Optional[str] = None
    intended_use: Optional[str] = None
    out_of_scope_use: Optional[str] = None
    training_data_desc: Optional[str] = None
    evaluation_data: Optional[str] = None
    performance_summary: Optional[Dict[str, Any]] = None
    fairness_summary: Optional[Dict[str, Any]] = None
    limitations: Optional[str] = None
    recommendations: Optional[str] = None

class ModelCardOut(BaseModel):
    id: str
    audit_id: str
    model_name: Optional[str]
    intended_use: Optional[str]
    out_of_scope_use: Optional[str]
    training_data_desc: Optional[str]
    evaluation_data: Optional[str]
    performance_summary: Optional[Dict[str, Any]]
    fairness_summary: Optional[Dict[str, Any]]
    limitations: Optional[str]
    recommendations: Optional[str]
    generated_at: datetime

    model_config = {"from_attributes": True}
