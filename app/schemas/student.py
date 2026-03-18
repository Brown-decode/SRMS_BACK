from pydantic import BaseModel
from datetime import datetime
from app.models.student import Gender
from typing import Optional    
class StudentCreate(BaseModel):
    class_id: Optional[int]
    date_of_birth: datetime
    gender: Gender
    
    class Config:
        from_attributes = True
    
class StudentResponse(StudentCreate):
    id: int
    full_name: str
    user_id: int
    class_id: int
    date_of_birth: datetime
    gender: str
        
    class Config:
        from_attributes = True
        
            


    