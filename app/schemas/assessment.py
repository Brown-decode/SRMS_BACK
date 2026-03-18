from pydantic import BaseModel
from typing import Optional
from datetime import date
from typing import List, Optional

class StudentScoreRow(BaseModel):
    student_id: int
    student_name: str
    score: Optional[float] = None  # Using float/Optional since it could be null

class AssessmentScoresResponse(BaseModel):
    assessment_id: int
    assessment_title: str
    max_score: float
    students: List[StudentScoreRow]
    
    class Config:
        from_attributes = True

class AssessmentBase(BaseModel):
    title: str
    description: Optional[str]
    class_subject_id: int
    term: int
    sequence: int
    max_score: float
    date: date

class AssessmentCreateRequest(AssessmentBase):
    pass
class AssessmentCreateResponse(AssessmentBase):
    id: int    

    class Config:
        from_attributes = True