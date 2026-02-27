from pydantic import BaseModel


class SubjectCreateRequest(BaseModel):
    name: str