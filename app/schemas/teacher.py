from pydantic import BaseModel

class TeacherResponse(BaseModel):
    id: int
    user_id: int
    full_name: str
    loginid: str
    
    class Config:
        from_attributes = True