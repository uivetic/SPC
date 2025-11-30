"""Activity models"""
from pydantic import BaseModel
from typing import Dict, List, Optional, Any


class ActivityOption(BaseModel):
    """Activity option model"""
    value: str
    label: str


class ActivityCategory(BaseModel):
    """Activity category model"""
    category: str  # 'o', 'h', 'p'
    name: str  # 'Opšte', 'HR', 'Projekti'
    activities: Dict[str, Any]  # Activity name -> roles/points mapping (can be dict or list)


class ActivityResponse(BaseModel):
    """Response model for activities"""
    categories: List[ActivityCategory]

