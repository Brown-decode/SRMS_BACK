from pydantic import BaseModel
from datetime import datetime
from app.models.student import Gender
from typing import List


class StudentCreate(BaseModel):
    full_name: str
    matricule: str
    class_id: int
    date_of_birth: datetime
    gender: Gender

    class Config:
        from_attributes = True


class StudentResponse(StudentCreate):
    id: int
    user_id: int
    
    class Config:
        from_attributes = True


class SubjectSummary(BaseModel):
    subject_name: str
    coefficient: int
    average: float  # The average for this specific subject


class StudentReportCard(BaseModel):
    student_name: str
    matricule: str
    average: float
    subjects: List[SubjectSummary]  # List of the model above
    promotion_status: str  # "PROMOTED" or "REPEAT"

    class Config:
        from_attributes = True


class StudentRank(BaseModel):
    student_name: str
    matricule: str
    average: float
    position: int

    class Config:
        from_attributes = True
