from pydantic import BaseModel
from app.models.class_model import Class
from app.models.class_model import Cycle, Stream


class ClassBase(BaseModel):
    name: str
    level: Cycle
    stream: Stream

    class Config:
        from_attributes = True

class ClassCreateRequest(ClassBase):
    pass

class ClassCreateResponse(ClassBase):
    id: int

    class Config:
        from_attributes = True