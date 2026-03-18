from pydantic import BaseModel

class TeacherResponse(BaseModel):
    id: int
    user_id: int
    username: str
    

    class Config:
        from_attributes = True