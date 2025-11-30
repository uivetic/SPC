"""Points models"""
from pydantic import BaseModel
from typing import List, Optional


class PointsWriteRequest(BaseModel):
    """Request model for writing points"""
    batch: List[List[str]]  # [opsteData, HRData, projektiData]
    pairs: List[List[str]]  # [[name, points], ...] - using List for JSON compatibility


class PointsResponse(BaseModel):
    """Response model for points"""
    hr: str = "0"
    opste: str = "0"
    projekti: str = "0"
    ukupno: str = "0"
    status: str = ""


class PointsWriteResponse(BaseModel):
    """Response model for write operation"""
    success: bool
    message: str
    count: int

