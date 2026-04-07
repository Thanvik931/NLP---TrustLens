"""Pydantic schemas for Audits."""
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

class AuditTriggerRequest(BaseModel):
    dataset_id: str
    model_id: str

class AuditRunOut(BaseModel):
    id: str
    dataset_id: str
    model_id: str
    triggered_by: Optional[str]
    status: str
    progress: int
    demographic_parity: Optional[float]
    equalized_odds_tpr: Optional[float]
    equalized_odds_fpr: Optional[float]
    disparate_impact: Optional[float]
    overall_accuracy: Optional[float]
    started_at: datetime
    completed_at: Optional[datetime]

    model_config = {"from_attributes": True}
