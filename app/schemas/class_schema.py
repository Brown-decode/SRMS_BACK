from pydantic import BaseModel
from ap.models.class_model import Class

class ClassCreateRequest(BaseModel):
    name: ClassName
    level: Cycle
    stream: Stream
    
    class Config:
        from_attributes = True