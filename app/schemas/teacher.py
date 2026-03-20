from pydantic import BaseModel
from typing import Optional


class TeacherResponse(BaseModel):
    id: int
    user_id: int
    full_name: str
    loginid: str

    class Config:
        from_attributes = True


class TeacherUpdate(BaseModel):
    full_name: Optional[str] = None
    loginid: Optional[str] = None

    class Config:
        from_attributes = True
