from pydantic import BaseModel

class TeacherCreateRequest(BaseModel):
    user_id: int
    
    class Config:
        from_attributes = True