from pydantic import BaseModel


class SubjectCreateRequest(BaseModel):
    name: str
    
class SubjectCreateResponse(BaseModel):
    id: int
    name: str