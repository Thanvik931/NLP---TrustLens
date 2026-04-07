"""Pydantic schemas for MLModel."""
from typing import Optional
from pydantic import BaseModel

class MLModelOut(BaseModel):
    id: str
    name: str
    framework: str
    domain: str
    description: Optional[str] = None
    model_file: Optional[str] = None
    is_active: bool
    created_at: str

    model_config = {"from_attributes": True}

class MLModelCreate(BaseModel):
    name: str
    framework: str
    domain: str
    description: Optional[str] = None
    model_file: Optional[str] = None
