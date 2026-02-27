from pydantic import BaseModel, EmailStr
from app.models.student import Gender
class StudentCreate(BaseModel):
    class_id: int
    date_of_birth: str
    gender: Gender
    
    class Config:
        from_attributes = True
    
class StudentResponse(StudentCreate):
    id: int
    full_name: str
    user_id: int
    class_id: int
    date_of_birth: str
    gender: str
        
    class Config:
        from_attributes = True
        
            


    