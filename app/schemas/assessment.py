from pydantic import BaseModel
from typing import Optional
from datetime import date


class AssessmentCreateRequest(BaseModel):
    title: str
    description: Optional[str]
    class_subject_id: int
    term: int
    sequence: int
    max_score: float
    date: date
    
    class Config:
        from_attributes = True
        
class AssessmentUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    max_score: Optional[float] = None
    date: Optional[date] = None

    class Config:
        from_attributes = True
