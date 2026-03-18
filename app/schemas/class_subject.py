from pydantic import BaseModel


class ClassSubjectBase(BaseModel):
    class_id: int
    subject_id: int
    teacher_id: int
    coefficient: float

class ClassSubjectCreateRequest(ClassSubjectBase):
    pass

class ClassSubjectCreateResponse(ClassSubjectBase):
    id: int

    class Config:
        from_attributes = True

