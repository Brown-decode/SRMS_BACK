from pydantic import BaseModel
from app.models.class_model import Class
from app.models.class_model import ClassName, Cycle, Stream
class ClassCreateRequest(BaseModel):
    name: ClassName
    level: Cycle
    stream: Stream
    
    class Config:
        from_attributes = True